from dataclasses import dataclass
from typing import override

from quark.core import Core, Result, Data
from quark.interface_types import InterfaceType, Graph, Other

import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


@dataclass
class GraphVisualizer(Core):
    """
    This is an example module following the recommended structure for a quark module.

    A module must have a preprocess and postprocess method, as required by the Core abstract base class.
    A module's interface is defined by the type of data parameter those methods receive and return, dictating which other modules it can be connected to.
    Types defining interfaces should be chosen form QUARKs predefined set of types to ensure compatibility with other modules. TODO: insert link
    """

    highlight_nodes: bool = False
    highlight_edges: bool = False
    node_size: int = 300
    node_shape: str = "o"
    edge_width: float = 1.0
    edge_style: str = "solid"
    font_size: int = 12
    solution_type: str = "path"
    save_path: str = ""
    show_plot: bool = True

    @override
    def preprocess(self, data: Graph) -> Result:
        self.g = data.as_nx_graph()
        return Data(data)

    @override
    def postprocess(self, data: Other[list]) -> Result:
        included_nodes = [node for node in self.g.nodes() if node in data.data]
        excluded_nodes = [node for node in self.g.nodes() if node not in data.data]
        pos = nx.spring_layout(self.g)
        included_pos = {n: n for n, _ in pos.items() if n in data.data}
        excluded_pos = {n: n for n, _ in pos.items() if n not in data.data}
        if self.solution_type == "path":
            edge_list = [(data.data[i], data.data[i + 1]) for i in range(len(data.data) - 1)]
            if len(data.data) > 2:
                edge_list.append((data.data[-1], data.data[0]))
            included_edges = [e for e in self.g.edges() if e in edge_list or (e[1], e[0]) in edge_list]
            excluded_edges = [e for e in self.g.edges() if e not in included_edges]
        elif self.solution_type == "set":
            included_edges = [e for e in self.g.edges() if e[0] in data.data and e[1] in data.data]
            excluded_edges = [e for e in self.g.edges() if e not in included_edges]
        else:
            raise ValueError(f"solution_type must be 'path' or 'set', and not {self.solution_type}")
        if self.highlight_nodes:
            mark_solution_nodes = "red"
        else:
            mark_solution_nodes = "black"
        if self.highlight_edges:
            mark_solution_edges = "red"
        else:
            mark_solution_edges = "black"
        legend_elements = [
            Line2D(
                [0],
                [0],
                marker=self.node_shape,
                ls=self.edge_style,
                color=mark_solution_edges,
                label="Included",
                markerfacecolor=mark_solution_nodes,
                markeredgewidth=0,
                markersize=10),
            Line2D(
                [0],
                [0],
                marker=self.node_shape,
                ls=self.edge_style,
                color="black",
                label="Excluded",
                markerfacecolor="black",
                markeredgewidth=0,
                markersize=10)
        ]
        nx.draw_networkx_nodes(
            self.g,
            pos,
            nodelist=included_nodes,
            node_size=self.node_size,
            node_color=mark_solution_nodes,
        )
        nx.draw_networkx_nodes(
            self.g,
            pos,
            nodelist=excluded_nodes,
            node_size=self.node_size,
            node_color="black",
        )
        nx.draw_networkx_labels(self.g, pos, included_pos, font_size=self.font_size, font_weight="bold", font_color="white")
        nx.draw_networkx_labels(self.g, pos, excluded_pos, font_size=self.font_size, font_color="white")
        nx.draw_networkx_edges(self.g, pos, edgelist=excluded_edges, width=self.edge_width*0.8, edge_color="black")
        nx.draw_networkx_edges(self.g, pos, edgelist=included_edges, width=self.edge_width, edge_color=mark_solution_edges)
        if self.highlight_nodes or self.highlight_edges:
            plt.legend(handles=legend_elements, loc="best")
        if self.save_path != "":
            plt.savefig(self.save_path)
        if self.show_plot:
            plt.show()
        return Data(data)
