from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QColor, QPen, QBrush, QTransform
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsLineItem
from Core.graph import Graph, Vertex, Edge

class CustomEllipse(QGraphicsEllipseItem):
    """Класс для вершины, который обновляет рёбра при перемещении."""

    def __init__(self, vertex_id, canvas, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vertex_id = vertex_id
        self.canvas = canvas
        self.setFlag(QGraphicsEllipseItem.ItemIsMovable)
        self.setFlag(QGraphicsEllipseItem.ItemSendsGeometryChanges)

    def itemChange(self, change, value):
        """Отслеживает изменения позиции элемента."""
        if change == QGraphicsEllipseItem.ItemPositionChange:
            self.canvas.update_edges(self.vertex_id)  
            self.canvas.save_vertex_position(self.vertex_id, value)
            vertex = self.canvas.graph.vertices[self.vertex_id]
            vertex.x, vertex.y = value.x(), value.y()
        return super().itemChange(change, value)


class Canvas(QGraphicsView):
    """Класс для визуализации графа."""

    def __init__(self, graph, parent=None):
        super().__init__(parent)
        self.graph = graph  
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.graph_changing_mode = False  
        self.available_ids = []  
        self.selected_vertices = []  
        self.canvas_width = self.width() 
        self.canvas_height = self.height()  
    
    def resizeEvent(self, event):
        """Обработчик события изменения размера холста."""
        super().resizeEvent(event)  
        self.canvas_width = self.width()
        self.canvas_height = self.height()

    def get_canvas_size(self):
        """Возвращает актуальные размеры текущего холста (ширина и высота)."""
        return self.canvas_width, self.canvas_height

    def enable_graph_changing_mode(self, enabled):
        """Включает или выключает режим редактирования графа."""
        self.graph_changing_mode = enabled

    def mousePressEvent(self, event):
        """Обрабатывает нажатия мыши на холсте."""
        if not self.graph_changing_mode:
            super().mousePressEvent(event)  
            return

        position = self.mapToScene(event.pos())  
        item = self.scene.itemAt(position, QTransform())  

        if event.modifiers() == Qt.ShiftModifier and event.button() == Qt.RightButton and isinstance(item, QGraphicsEllipseItem):
            self.select_vertex(item)
        elif event.button() == Qt.RightButton and event.modifiers() == Qt.AltModifier:
            if isinstance(item, QGraphicsEllipseItem):
                self.delete_vertex(item)
            elif isinstance(item, QGraphicsLineItem):
                self.delete_edge(item)
        elif event.button() == Qt.RightButton and event.modifiers() == Qt.ControlModifier:
            self.create_vertex(position)
        else:
            super().mousePressEvent(event)

    def select_vertex(self, item):
        """Выделяет вершину и создаёт ребро, если выбрано две вершины.""" 
        vertex_id = item.data(0)
        if vertex_id in self.graph.vertices:
            vertex = self.graph.vertices[vertex_id]
            item.setBrush(QBrush(QColor(vertex.highlighted_params["color"])))
            self.selected_vertices.append(vertex_id)

            if len(self.selected_vertices) == 2:
                self.create_edge(self.selected_vertices[0], self.selected_vertices[1])
                for vid in self.selected_vertices:
                    vertex_item = self.graph.vertices[vid].item
                    vertex_item.setBrush(QBrush(QColor(self.graph.vertices[vid].default_params["color"])))
                self.selected_vertices = []

    def create_edge(self, start_id, end_id):
        """Создаёт ребро между двумя вершинами, заменяя существующее, если оно уже есть."""
        weight, ok = self.request_edge_weight()
        if not ok:
            return

        start_vertex = self.graph.vertices[start_id]
        end_vertex = self.graph.vertices[end_id]

        existing_edge = None
        for edge in self.graph.edges:
            if (edge.start_vertex == start_vertex and edge.end_vertex == end_vertex) or \
               (edge.start_vertex == end_vertex and edge.end_vertex == start_vertex):
                existing_edge = edge
                break
        
        if existing_edge:
            existing_edge.weight = weight  
            self.update_edge_visual(existing_edge) 
        else:
            edge = Edge(start_vertex, end_vertex, weight=weight)
            self.graph.edges.append(edge)
            self.create_edge_visual(edge)

    def update_edge_visual(self, edge):
        """Обновляет визуальное представление существующего рёбер.""" 
        start_pos = self.get_circle_edge_position(edge.start_vertex.item, edge.end_vertex.item)
        end_pos = self.get_circle_edge_position(edge.end_vertex.item, edge.start_vertex.item)

        if hasattr(edge, 'line_item'):
            edge.line_item.setLine(start_pos.x(), start_pos.y(), end_pos.x(), end_pos.y())

        if hasattr(edge, 'text_item'):
            mid_point = (start_pos + end_pos) / 2
            edge.text_item.setPos(mid_point.x() - edge.text_item.boundingRect().width() / 2,
                                  mid_point.y() - edge.text_item.boundingRect().height() / 2)
            edge.text_item.setPlainText(str(edge.weight))  

    def create_edge_visual(self, edge):
        """Создаёт визуальное представление ребра.""" 
        start_pos = self.get_circle_edge_position(edge.start_vertex.item, edge.end_vertex.item)
        end_pos = self.get_circle_edge_position(edge.end_vertex.item, edge.start_vertex.item)

        pen = QPen(QColor(edge.default_params["color"]), edge.default_params["thickness"])
        line_item = QGraphicsLineItem(start_pos.x(), start_pos.y(), end_pos.x(), end_pos.y())
        line_item.setPen(pen)
        self.scene.addItem(line_item)

        mid_point = (start_pos + end_pos) / 2
        text = QGraphicsTextItem(str(edge.weight))
        text.setDefaultTextColor(QColor(edge.default_params.get("text_color", "black")))
        text.setPos(mid_point.x() - text.boundingRect().width() / 2, mid_point.y() - text.boundingRect().height() / 2)
        self.scene.addItem(text)

        edge.line_item = line_item  
        edge.text_item = text  

    def create_edge_special(self, start_id, end_id, weight):
        """Создаёт или обновляет ребро между двумя вершинами."""
        
        existing_edge = None
        for edge in self.graph.edges:
            if (edge.start_vertex.id == start_id and edge.end_vertex.id == end_id) or \
            (edge.start_vertex.id == end_id and edge.end_vertex.id == start_id):
                existing_edge = edge
                break

        if existing_edge:
            existing_edge.weight = weight
            self.update_edge_visual(existing_edge)  
            print(f"Обновлено ребро между вершинами {start_id} и {end_id} с новым весом {weight}")
        else:
            start_vertex = self.graph.vertices[start_id]
            end_vertex = self.graph.vertices[end_id]
            edge = Edge(start_vertex, end_vertex, weight=weight)
            self.graph.edges.append(edge)
            self.create_edge_visual(edge)  

    def get_circle_edge_position(self, source_item, target_item):
        """Вычисляет точку пересечения рёбер с краем круга вершины.""" 
        source_center = source_item.sceneBoundingRect().center()
        target_center = target_item.sceneBoundingRect().center()

        dx = target_center.x() - source_center.x()
        dy = target_center.y() - source_center.y()
        distance = (dx ** 2 + dy ** 2) ** 0.5

        radius = source_item.rect().width() / 2 

        if distance == 0:
            return source_center

        offset_x = radius * dx / distance
        offset_y = radius * dy / distance

        return QPointF(source_center.x() + offset_x, source_center.y() + offset_y)

    def update_edges(self, vertex_id):
        """Обновляет все рёбра, связанные с вершиной.""" 
        vertex = self.graph.vertices[vertex_id]
        for edge in self.graph.edges:
            if edge.start_vertex == vertex or edge.end_vertex == vertex:
                start_pos = self.get_circle_edge_position(edge.start_vertex.item, edge.end_vertex.item)
                end_pos = self.get_circle_edge_position(edge.end_vertex.item, edge.start_vertex.item)

                if hasattr(edge, 'line_item'):
                    edge.line_item.setLine(start_pos.x(), start_pos.y(), end_pos.x(), end_pos.y())

                if hasattr(edge, 'text_item'):
                    mid_point = (start_pos + end_pos) / 2
                    edge.text_item.setPos(mid_point.x() - edge.text_item.boundingRect().width() / 2,
                                        mid_point.y() - edge.text_item.boundingRect().height() / 2)

    def save_vertex_position(self, vertex_id, position):
        """Сохраняет новые координаты вершины после её перемещения.""" 
        if vertex_id in self.graph.vertices:
            vertex = self.graph.vertices[vertex_id]
            vertex.x, vertex.y = position.x(), position.y()


    def create_vertex(self, position):
        """Создаёт вершину на холсте.""" 
        if self.available_ids:
            vertex_id = self.available_ids.pop(0)
        else:
            vertex_id = len(self.graph.vertices) + 1

        vertex = Vertex(vertex_id, x=position.x(), y=position.y())
        self.graph.add_vertex(vertex)

        color = QColor(vertex.default_params["color"])
        radius = vertex.default_params["size"]
        x, y = position.x(), position.y()

        ellipse = CustomEllipse(vertex_id, self, x - radius, y - radius, radius * 2, radius * 2)
        ellipse.setBrush(QBrush(color))
        ellipse.setData(0, vertex_id)

        text = QGraphicsTextItem(str(vertex_id))
        text.setParentItem(ellipse)
        text.setDefaultTextColor(QColor(vertex.default_params["text_color"]))
        text.setPos(
            ellipse.rect().center().x() - text.boundingRect().width() / 2,
            ellipse.rect().center().y() - text.boundingRect().height() / 2,
        )

        self.scene.addItem(ellipse)
        self.graph.vertices[vertex_id].item = ellipse
    
    def create_vertex_visual(self, vertex):
        """Создаёт визуальное представление вершины на холсте.""" 
        color = QColor(vertex.default_params["color"])
        radius = vertex.default_params["size"]
        x, y = vertex.x, vertex.y

        ellipse = CustomEllipse(vertex.id, self, x - radius, y - radius, radius * 2, radius * 2)
        ellipse.setBrush(QBrush(color))
        ellipse.setData(0, vertex.id)

        text = QGraphicsTextItem(str(vertex.id))
        text.setParentItem(ellipse)
        text.setDefaultTextColor(QColor(vertex.default_params["text_color"]))
        text.setPos(
            ellipse.rect().center().x() - text.boundingRect().width() / 2,
            ellipse.rect().center().y() - text.boundingRect().height() / 2,
        )

        self.scene.addItem(ellipse)
        self.graph.vertices[vertex.id].item = ellipse

    def delete_vertex(self, item):
        """Удаляет вершину по правому клику с Alt.""" 
        vertex_id = item.data(0)
        if vertex_id in self.graph.vertices:
            edges_to_remove = [edge for edge in self.graph.edges
                               if edge.start_vertex.id == vertex_id or edge.end_vertex.id == vertex_id]
            for edge in edges_to_remove:
                self.scene.removeItem(edge.line_item)
                self.scene.removeItem(edge.text_item)
                self.graph.edges.remove(edge)

            del self.graph.vertices[vertex_id]
            self.scene.removeItem(item)
            self.available_ids.append(vertex_id)
            self.available_ids.sort()
            self.update()

    def delete_edge(self, item):
        """Удаляет ребро по правому клику с Alt.""" 
        for edge in self.graph.edges:
            if edge.line_item == item:
                self.scene.removeItem(edge.line_item)
                self.scene.removeItem(edge.text_item)
                self.graph.edges.remove(edge)
                self.update()
                break

    def request_edge_weight(self):
        """Запрашивает у пользователя вес рёбер.""" 
        weight, ok = QtWidgets.QInputDialog.getInt(
            self, "Вес рёбер", "Введите вес рёбер:", 1, 1, 100, 1
        )
        return weight, ok

    def update(self):
        """Обновляет холст (перерисовывает его)."""
        self.scene.update()
