/**
 * kolmo_core.hpp — GraphRAG C++ core for kolmo_stats
 *
 * Pure C++17, no Python headers. Four components:
 *
 *   GraphIndex   — all precomputed lookup structures (O(1) per query)
 *   TFIDFIndex   — row-major float matrix, dot-product search (auto-vectorisable)
 *   bfs_traverse — scored BFS over the adjacency cache
 *   drift_search — semantic guided walk (edge weight + cosine similarity)
 */
#pragma once

#include <algorithm>
#include <cmath>
#include <numeric>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

namespace kolmo {

// ─────────────────────────────────────────────────────────────────────────────
// Utility
// ─────────────────────────────────────────────────────────────────────────────

static inline std::string to_lower(const std::string& s) {
    std::string r = s;
    for (char& c : r)
        c = static_cast<char>(std::tolower(static_cast<unsigned char>(c)));
    return r;
}

static inline std::vector<std::string> tokenize(const std::string& text) {
    std::vector<std::string> tokens;
    std::string tok;
    for (char c : text) {
        char lc = static_cast<char>(std::tolower(static_cast<unsigned char>(c)));
        if (std::isalnum(static_cast<unsigned char>(lc))) {
            tok += lc;
        } else {
            if (tok.size() > 1) tokens.push_back(tok);
            tok.clear();
        }
    }
    if (tok.size() > 1) tokens.push_back(tok);
    return tokens;
}

static inline std::string edge_key(const std::string& src, const std::string& tgt) {
    return src + "__" + tgt;
}

// ─────────────────────────────────────────────────────────────────────────────
// Data types
// ─────────────────────────────────────────────────────────────────────────────

struct EdgeData {
    float       weight   = 0.0f;
    int         sign     = 1;
    std::string label;
    std::string rationale;
};

struct AdjEntry {
    std::vector<std::string> drivers;
    std::vector<std::string> outputs;
    std::vector<std::string> hop2_drivers;
    std::vector<std::string> hop2_outputs;
};

struct NodeMeta {
    std::string              label;
    std::string              cluster;
    int                      tier = 3;
    std::string              unit;
    std::string              description;
    std::string              strategy_hint;
    std::vector<std::string> aliases;
    std::vector<std::string> formulas;
};

// ─────────────────────────────────────────────────────────────────────────────
// GraphIndex — O(1) lookup for everything
// ─────────────────────────────────────────────────────────────────────────────

class GraphIndex {
public:
    std::vector<std::string>                                    node_ids;
    std::unordered_map<std::string, NodeMeta>                   nodes;
    std::unordered_map<std::string, std::vector<std::string>>   token_index;
    std::unordered_map<std::string, std::string>                alias_index;
    std::unordered_map<std::string, std::vector<std::string>>   cluster_index;
    std::unordered_map<std::string, AdjEntry>                   adjacency;
    std::unordered_map<std::string, EdgeData>                   edges;        // "src__tgt"
    std::unordered_map<std::string, std::vector<std::string>>   node_formulas;
    std::unordered_map<std::string, std::vector<std::string>>   formula_index;

    void add_node(
        const std::string&              id,
        const std::string&              label,
        const std::string&              cluster,
        int                             tier,
        const std::string&              unit,
        const std::string&              description,
        const std::string&              strategy_hint,
        const std::vector<std::string>& aliases,
        const std::vector<std::string>& formulas
    ) {
        node_ids.push_back(id);
        nodes[id] = {label, cluster, tier, unit, description, strategy_hint, aliases, formulas};
        adjacency[id] = {};

        // Token inverted index
        std::string corpus = id + " " + label + " " + description + " " +
                             strategy_hint + " " + cluster;
        for (auto& a : aliases)  corpus += " " + a;
        for (auto& f : formulas) corpus += " " + f;
        for (auto& tok : tokenize(corpus))
            token_index[tok].push_back(id);

        // Alias index — O(1) exact resolution
        alias_index[to_lower(id)]    = id;
        alias_index[to_lower(label)] = id;
        for (auto& a : aliases) alias_index[to_lower(a)] = id;

        // Cluster index
        cluster_index[cluster].push_back(id);

        // Formula indices
        node_formulas[id] = formulas;
        for (auto& f : formulas) formula_index[f].push_back(id);
    }

    void add_edge(
        const std::string& src,
        const std::string& tgt,
        float weight, int sign,
        const std::string& label,
        const std::string& rationale
    ) {
        edges[edge_key(src, tgt)] = {weight, sign, label, rationale};
        adjacency[tgt].drivers.push_back(src);
        adjacency[src].outputs.push_back(tgt);
    }

    // Call once after all add_node / add_edge — precomputes 2-hop adjacency
    void finalize() {
        for (auto& id : node_ids) {
            auto& adj = adjacency[id];
            std::unordered_set<std::string> sd(adj.drivers.begin(), adj.drivers.end());
            std::unordered_set<std::string> so(adj.outputs.begin(), adj.outputs.end());
            sd.insert(id); so.insert(id);

            for (auto& d : adj.drivers)
                for (auto& d2 : adjacency[d].drivers)
                    if (sd.insert(d2).second)
                        adj.hop2_drivers.push_back(d2);

            for (auto& o : adj.outputs)
                for (auto& o2 : adjacency[o].outputs)
                    if (so.insert(o2).second)
                        adj.hop2_outputs.push_back(o2);
        }
    }

    // Token search — returns (node_id, hit_count) ranked by hits
    std::vector<std::pair<std::string, int>> token_search(
        const std::string& query, int top_k
    ) const {
        std::unordered_map<std::string, int> hits;
        for (auto& tok : tokenize(query)) {
            auto it = token_index.find(tok);
            if (it != token_index.end())
                for (auto& nid : it->second) hits[nid]++;
        }
        std::vector<std::pair<std::string, int>> ranked(hits.begin(), hits.end());
        int k = std::min(top_k, static_cast<int>(ranked.size()));
        std::partial_sort(ranked.begin(), ranked.begin() + k, ranked.end(),
            [](const auto& a, const auto& b) { return a.second > b.second; });
        ranked.resize(k);
        return ranked;
    }

    std::string resolve_alias(const std::string& raw) const {
        auto it = alias_index.find(to_lower(raw));
        return (it != alias_index.end()) ? it->second : std::string{};
    }

    bool has_edge(const std::string& src, const std::string& tgt) const {
        return edges.count(edge_key(src, tgt)) > 0;
    }

    const EdgeData* get_edge(const std::string& src, const std::string& tgt) const {
        auto it = edges.find(edge_key(src, tgt));
        return (it != edges.end()) ? &it->second : nullptr;
    }

    std::string node_text(const std::string& id) const {
        auto it = nodes.find(id);
        if (it == nodes.end()) return {};
        const auto& m = it->second;
        std::string t = m.label + " " + m.description + " " + m.strategy_hint + " " + m.cluster;
        for (auto& a : m.aliases)  t += " " + a;
        for (auto& f : m.formulas) t += " " + f;
        return t;
    }
};

// ─────────────────────────────────────────────────────────────────────────────
// TFIDFIndex — row-major float matrix, compiler-vectorisable dot products
// ─────────────────────────────────────────────────────────────────────────────

class TFIDFIndex {
public:
    std::vector<std::string>             node_ids;
    std::unordered_map<std::string, int> vocab;
    std::vector<float>                   matrix;   // row-major, N × V, L2-normalised
    int N = 0, V = 0;

    void build(const std::vector<std::string>& ids,
               const std::vector<std::string>& texts) {
        node_ids = ids;
        N = static_cast<int>(ids.size());

        std::vector<std::vector<std::string>> tok(N);
        std::unordered_set<std::string> all_toks;
        for (int i = 0; i < N; i++) {
            tok[i] = tokenize(texts[i]);
            all_toks.insert(tok[i].begin(), tok[i].end());
        }

        std::vector<std::string> vocab_list(all_toks.begin(), all_toks.end());
        std::sort(vocab_list.begin(), vocab_list.end());
        vocab.reserve(vocab_list.size());
        for (int j = 0; j < static_cast<int>(vocab_list.size()); j++)
            vocab[vocab_list[j]] = j;
        V = static_cast<int>(vocab_list.size());

        // TF
        matrix.assign(static_cast<std::size_t>(N) * V, 0.0f);
        for (int i = 0; i < N; i++) {
            for (auto& t : tok[i]) {
                auto it = vocab.find(t);
                if (it != vocab.end()) matrix[i * V + it->second] += 1.0f;
            }
            float s = 0.0f;
            for (int j = 0; j < V; j++) s += matrix[i * V + j];
            if (s > 0.0f)
                for (int j = 0; j < V; j++) matrix[i * V + j] /= s;
        }

        // IDF
        std::vector<float> idf(V);
        for (int j = 0; j < V; j++) {
            int df = 0;
            for (int i = 0; i < N; i++) if (matrix[i * V + j] > 0.0f) df++;
            idf[j] = std::log((N + 1.0f) / (df + 1.0f)) + 1.0f;
        }
        for (int i = 0; i < N; i++)
            for (int j = 0; j < V; j++) matrix[i * V + j] *= idf[j];

        // L2 normalise — each row becomes a unit vector
        for (int i = 0; i < N; i++) {
            float norm = 0.0f;
            for (int j = 0; j < V; j++) norm += matrix[i * V + j] * matrix[i * V + j];
            norm = std::sqrt(norm);
            if (norm > 0.0f)
                for (int j = 0; j < V; j++) matrix[i * V + j] /= norm;
        }
    }

    std::vector<float> embed_query(const std::string& query) const {
        std::vector<float> vec(V, 0.0f);
        for (auto& tok : tokenize(query)) {
            auto it = vocab.find(tok);
            if (it != vocab.end()) vec[it->second] += 1.0f;
        }
        float s = 0.0f;
        for (float v : vec) s += v;
        if (s > 0.0f) for (float& v : vec) v /= s;
        float norm = 0.0f;
        for (float v : vec) norm += v * v;
        norm = std::sqrt(norm);
        if (norm > 0.0f) for (float& v : vec) v /= norm;
        return vec;
    }

    // Inner dot product — this loop auto-vectorises to AVX2 with -O3 -march=native
    float dot(int node_idx, const std::vector<float>& qvec) const {
        float result = 0.0f;
        const float* row = matrix.data() + node_idx * V;
        const float* q   = qvec.data();
        for (int j = 0; j < V; j++) result += row[j] * q[j];
        return result;
    }

    // Top-K via partial_sort — O(N log K)
    std::vector<std::pair<std::string, float>> top_k(const std::string& query, int k) const {
        return top_k_vec(embed_query(query), k);
    }

    std::vector<std::pair<std::string, float>> top_k_vec(
        const std::vector<float>& qvec, int k
    ) const {
        std::vector<std::pair<int, float>> scores(N);
        for (int i = 0; i < N; i++) scores[i] = {i, dot(i, qvec)};
        int ek = std::min(k, N);
        std::partial_sort(scores.begin(), scores.begin() + ek, scores.end(),
            [](const auto& a, const auto& b) { return a.second > b.second; });
        std::vector<std::pair<std::string, float>> out;
        out.reserve(ek);
        for (int i = 0; i < ek; i++)
            if (scores[i].second > 0.0f)
                out.push_back({node_ids[scores[i].first], scores[i].second});
        return out;
    }

    float node_similarity(const std::string& id, const std::vector<float>& qvec) const {
        auto it = std::find(node_ids.begin(), node_ids.end(), id);
        if (it == node_ids.end()) return 0.0f;
        return dot(static_cast<int>(std::distance(node_ids.begin(), it)), qvec);
    }
};

// ─────────────────────────────────────────────────────────────────────────────
// BFS traversal — scored, depth-limited, over the adjacency cache
// ─────────────────────────────────────────────────────────────────────────────

inline std::unordered_map<std::string, float> bfs_traverse(
    const GraphIndex&                               idx,
    const std::vector<std::pair<std::string, float>>& seeds,
    int   depth,
    float decay = 0.65f
) {
    std::unordered_map<std::string, float> visited;
    visited.reserve(64);

    for (auto& [seed_id, seed_score] : seeds) {
        auto& slot = visited[seed_id];
        slot = std::max(slot, seed_score);

        std::vector<std::string> frontier = {seed_id};
        for (int d = 0; d < depth; d++) {
            float d_score = seed_score * std::pow(decay, d + 1);
            std::vector<std::string> next;
            next.reserve(frontier.size() * 4);

            for (auto& nid : frontier) {
                auto it = idx.adjacency.find(nid);
                if (it == idx.adjacency.end()) continue;
                const auto& adj = it->second;
                auto absorb = [&](const std::vector<std::string>& nbrs) {
                    for (auto& nb : nbrs) {
                        auto& s = visited[nb];
                        s = std::max(s, d_score);
                        next.push_back(nb);
                    }
                };
                absorb(adj.drivers);
                absorb(adj.outputs);
            }
            frontier = std::move(next);
        }
    }
    return visited;
}

// ─────────────────────────────────────────────────────────────────────────────
// Drift search — guided walk: edge_weight * 0.6 + cosine_sim * 0.4
// ─────────────────────────────────────────────────────────────────────────────

inline std::vector<std::string> drift_search(
    const GraphIndex&          idx,
    const TFIDFIndex&          emb,
    const std::string&         start,
    const std::vector<float>&  query_vec,
    int                        steps
) {
    std::vector<std::string>    path = {start};
    std::unordered_set<std::string> visited = {start};
    std::string current = start;

    for (int s = 0; s < steps; s++) {
        auto it = idx.adjacency.find(current);
        if (it == idx.adjacency.end()) break;

        const auto& adj = it->second;
        std::vector<std::string> candidates;
        candidates.reserve(adj.drivers.size() + adj.outputs.size());
        for (auto& n : adj.drivers)  if (!visited.count(n)) candidates.push_back(n);
        for (auto& n : adj.outputs)  if (!visited.count(n)) candidates.push_back(n);
        if (candidates.empty()) break;

        std::string best;
        float best_score = -1.0f;
        for (auto& c : candidates) {
            float ew = 0.0f;
            if (auto* e = idx.get_edge(current, c)) ew = e->weight;
            else if (auto* e = idx.get_edge(c, current)) ew = e->weight;
            float score = 0.6f * ew + 0.4f * emb.node_similarity(c, query_vec);
            if (score > best_score) { best_score = score; best = c; }
        }
        if (best.empty()) break;

        path.push_back(best);
        visited.insert(best);
        current = best;
    }
    return path;
}

} // namespace kolmo
