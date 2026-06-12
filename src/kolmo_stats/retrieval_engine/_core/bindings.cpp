/**
 * pybind11 module: kolmo_stats.retrieval_engine._core
 *
 * Exposes GraphIndex, TFIDFIndex, bfs_traverse, drift_search to Python.
 * All STL containers auto-convert to Python via pybind11/stl.h.
 */
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "kolmo_core.hpp"

namespace py = pybind11;
using namespace kolmo;

PYBIND11_MODULE(_core, m) {
    m.doc() = "kolmo_stats GraphRAG C++ core — GraphIndex, TFIDFIndex, BFS, drift";

    // ── NodeMeta ──────────────────────────────────────────────────────────────
    py::class_<NodeMeta>(m, "NodeMeta")
        .def_readonly("label",         &NodeMeta::label)
        .def_readonly("cluster",       &NodeMeta::cluster)
        .def_readonly("tier",          &NodeMeta::tier)
        .def_readonly("unit",          &NodeMeta::unit)
        .def_readonly("description",   &NodeMeta::description)
        .def_readonly("strategy_hint", &NodeMeta::strategy_hint)
        .def_readonly("aliases",       &NodeMeta::aliases)
        .def_readonly("formulas",      &NodeMeta::formulas)
        .def("__repr__", [](const NodeMeta& m) {
            return "<NodeMeta label=" + m.label + " cluster=" + m.cluster + ">";
        });

    // ── EdgeData ──────────────────────────────────────────────────────────────
    py::class_<EdgeData>(m, "EdgeData")
        .def_readonly("weight",    &EdgeData::weight)
        .def_readonly("sign",      &EdgeData::sign)
        .def_readonly("label",     &EdgeData::label)
        .def_readonly("rationale", &EdgeData::rationale);

    // ── AdjEntry ──────────────────────────────────────────────────────────────
    py::class_<AdjEntry>(m, "AdjEntry")
        .def_readonly("drivers",      &AdjEntry::drivers)
        .def_readonly("outputs",      &AdjEntry::outputs)
        .def_readonly("hop2_drivers", &AdjEntry::hop2_drivers)
        .def_readonly("hop2_outputs", &AdjEntry::hop2_outputs);

    // ── GraphIndex ────────────────────────────────────────────────────────────
    py::class_<GraphIndex>(m, "GraphIndex")
        .def(py::init<>())
        .def("add_node",      &GraphIndex::add_node,
             py::arg("id"), py::arg("label"), py::arg("cluster"),
             py::arg("tier"), py::arg("unit"), py::arg("description"),
             py::arg("strategy_hint"), py::arg("aliases"), py::arg("formulas"))
        .def("add_edge",      &GraphIndex::add_edge,
             py::arg("src"), py::arg("tgt"), py::arg("weight"),
             py::arg("sign"), py::arg("label"), py::arg("rationale"))
        .def("finalize",      &GraphIndex::finalize)
        .def("token_search",  &GraphIndex::token_search,
             py::arg("query"), py::arg("top_k"))
        .def("resolve_alias", &GraphIndex::resolve_alias, py::arg("raw"))
        .def("has_edge",      &GraphIndex::has_edge,
             py::arg("src"), py::arg("tgt"))
        .def("get_edge", [](const GraphIndex& g, const std::string& s, const std::string& t)
             -> py::object {
                 auto* e = g.get_edge(s, t);
                 return e ? py::cast(*e) : py::none();
             }, py::arg("src"), py::arg("tgt"))
        .def("node_text",     &GraphIndex::node_text, py::arg("id"))
        // Read-only attribute access
        .def_readonly("node_ids",      &GraphIndex::node_ids)
        .def_readonly("nodes",         &GraphIndex::nodes)
        .def_readonly("adjacency",     &GraphIndex::adjacency)
        .def_readonly("cluster_index", &GraphIndex::cluster_index)
        .def_readonly("node_formulas", &GraphIndex::node_formulas)
        .def_readonly("formula_index", &GraphIndex::formula_index)
        .def("__len__", [](const GraphIndex& g) { return g.node_ids.size(); })
        .def("__repr__", [](const GraphIndex& g) {
            return "<GraphIndex nodes=" + std::to_string(g.node_ids.size()) +
                   " edges=" + std::to_string(g.edges.size()) + ">";
        });

    // ── TFIDFIndex ────────────────────────────────────────────────────────────
    py::class_<TFIDFIndex>(m, "TFIDFIndex")
        .def(py::init<>())
        .def("build",            &TFIDFIndex::build,
             py::arg("ids"), py::arg("texts"))
        .def("embed_query",      &TFIDFIndex::embed_query, py::arg("query"))
        .def("top_k",            &TFIDFIndex::top_k,
             py::arg("query"), py::arg("k"))
        .def("top_k_vec",        &TFIDFIndex::top_k_vec,
             py::arg("qvec"), py::arg("k"))
        .def("node_similarity",  &TFIDFIndex::node_similarity,
             py::arg("node_id"), py::arg("qvec"))
        .def_readonly("node_ids", &TFIDFIndex::node_ids)
        .def_readonly("N",        &TFIDFIndex::N)
        .def_readonly("V",        &TFIDFIndex::V)
        .def("__repr__", [](const TFIDFIndex& t) {
            return "<TFIDFIndex N=" + std::to_string(t.N) +
                   " V=" + std::to_string(t.V) + ">";
        });

    // ── Free functions ────────────────────────────────────────────────────────
    m.def("bfs_traverse",
        [](const GraphIndex& idx,
           const std::vector<std::pair<std::string, float>>& seeds,
           int depth, float decay) {
            return bfs_traverse(idx, seeds, depth, decay);
        },
        py::arg("index"), py::arg("seeds"), py::arg("depth"), py::arg("decay") = 0.65f,
        "Scored BFS over the precomputed adjacency cache. "
        "Returns dict[node_id, score].");

    m.def("drift_search",
        [](const GraphIndex& idx,
           const TFIDFIndex& emb,
           const std::string& start,
           const std::vector<float>& qvec,
           int steps) {
            return drift_search(idx, emb, start, qvec, steps);
        },
        py::arg("index"), py::arg("embedder"), py::arg("start"),
        py::arg("query_vec"), py::arg("steps"),
        "Semantic guided walk: at each step picks the neighbour with highest "
        "0.6*edge_weight + 0.4*cosine_similarity. Returns ordered path.");
}
