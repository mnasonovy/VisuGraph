class Vertex:
    def __init__(self, id, x=0, y=0, canvas=None, is_highlighted=False):
        self.id = id  
        self.x = x  
        self.y = y 
        self.canvas = canvas  
        self.is_highlighted = is_highlighted  
        self.default_params = {
            "color": "white",
            "border_color": "blue",
            "border_width": 10,
            "text_size": 20,
            "text_color": "green",
            "shape": "circle",
            "size": 20
        }
        self.highlighted_params = {
            "color": "#7FFFD4",
            "border_color": "black",
            "border_width": 3,
            "text_size": 14,
            "text_color": "white",
            "shape": "circle",
            "size": 25
        }

        self.update_params()
    def update_params(self):
        """Метод для применения параметров в зависимости от выделенности"""
        if self.is_highlighted:
            self.params = self.highlighted_params.copy()
        else:
            self.params = self.default_params.copy()

    def set_highlighted(self, is_highlighted):
        """Метод для изменения флага выделенности"""
        self.is_highlighted = is_highlighted
        self.update_params()

    def update_custom_params(self, color=None, border_color=None, border_width=None, 
                             text_size=None, text_color=None, shape=None, size=None):
        """Метод для изменения параметров вершины напрямую"""
        target_params = self.highlighted_params if self.is_highlighted else self.default_params
        if color:
            target_params["color"] = color
        if border_color:
            target_params["border_color"] = border_color
        if border_width:
            target_params["border_width"] = border_width
        if text_size:
            target_params["text_size"] = text_size
        if text_color:
            target_params["text_color"] = text_color
        if shape:
            target_params["shape"] = shape
        if size:
            target_params["size"] = size

class Edge:
    def __init__(self, start_vertex, end_vertex, weight=1, is_highlighted=False):
        self.start_vertex = start_vertex  
        self.end_vertex = end_vertex  
        self.weight = weight 
        self.is_highlighted = is_highlighted  
        self.default_params = {
            "color": "#DB7093",
            "text_size": 10,
            "text_color": "green",
            "style": "solid",
            "thickness": 2
        }
        self.highlighted_params = {
            "color": "red",
            "text_size": 12,
            "text_color": "green",
            "style": "dashed",
            "thickness": 3
        }

        self.update_params()

    def update_params(self):
        """Метод для применения параметров в зависимости от выделенности"""
        if self.is_highlighted:
            self.params = self.highlighted_params.copy()
        else:
            self.params = self.default_params.copy()

    def set_highlighted(self, is_highlighted):
        """Метод для изменения флага выделенности"""
        self.is_highlighted = is_highlighted
        self.update_params()

    def update_custom_params(self, color=None, text_size=None, style=None, thickness=None):
        """Метод для изменения параметров ребра напрямую"""
        target_params = self.highlighted_params if self.is_highlighted else self.default_params
        if color:
            target_params["color"] = color
        if text_size:
            target_params["text_size"] = text_size
        if style:
            target_params["style"] = style
        if thickness:
            target_params["thickness"] = thickness


class Graph:
    def __init__(self):
        self.vertices = {}  
        self.edges = []  

    def add_vertex(self, vertex):
        """Добавление вершины в граф"""
        self.vertices[vertex.id] = vertex

    def add_edge(self, start_vertex, end_vertex, weight=1):
        """Добавление ребра в граф или замена существующего"""
        existing_edge = None
        for edge in self.edges:
            if (edge.start_vertex == start_vertex and edge.end_vertex == end_vertex) or \
               (edge.start_vertex == end_vertex and edge.end_vertex == start_vertex):
                existing_edge = edge
                break
        if existing_edge:
            existing_edge.weight = weight
            existing_edge.update_params()  
        else:
            new_edge = Edge(start_vertex, end_vertex, weight)
            self.edges.append(new_edge)

    def update_global_vertex_params(self, color=None, border_color=None, border_width=None, 
                                    text_size=None, text_color=None, shape=None, size=None, is_highlighted=False):
        """Обновление глобальных параметров для всех вершин"""
        for vertex in self.vertices.values():
            if vertex.is_highlighted == is_highlighted:  
                vertex.update_custom_params(color, border_color, border_width, text_size, text_color, shape, size)

    def update_global_edge_params(self, color=None, text_size=None, style=None, thickness=None, is_highlighted=False):
        """Обновление глобальных параметров для всех рёбер"""
        for edge in self.edges:
            if edge.is_highlighted == is_highlighted:  
                edge.update_custom_params(color, text_size, style, thickness)

