import pygame
import pygame_gui
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import random
import cProfile
import time
import pstats
from pygame_gui.elements import UIWindow

class PhysicsObject:
    def __init__(self, mass, position, velocity, shape='circle', color=None, elasticity=0.8):
        self.mass = mass
        self.position = np.array(position, dtype=float)
        self.velocity = np.array(velocity, dtype=float)
        self.shape = shape
        self.color = color or (np.random.randint(0, 255), np.random.randint(0, 255), np.random.randint(0, 255))
        self.elasticity = elasticity
        self.trail = []
        

    def update(self, dt, gravity, air_resistance):
        self.velocity[1] -= gravity * dt
        self.velocity -= air_resistance * self.velocity * dt
        self.position += self.velocity * dt
        self.trail.append(self.position.copy())
        if len(self.trail) > 50:
            self.trail.pop(0)

    @property
    def kinetic_energy(self):
        return 0.5 * self.mass * np.sum(self.velocity**2)

    @property
    def momentum(self):
        return self.mass * self.velocity

class Obstacle:
    def __init__(self, position, size):
        self.position = np.array(position)
        self.size = np.array(size)

    def collides_with(self, obj):
        return np.all(np.abs(obj.position - self.position) < (self.size + 1) / 2)

class Simulation:
    def __init__(self):
        self.objects = []
        self.obstacles = []
        self.time = 0
        self.gravity = 9.8
        self.air_resistance = 0.1
        self.paused = False

    def add_object(self, obj):
        self.objects.append(obj)

    def add_obstacle(self, obstacle):
        self.obstacles.append(obstacle)

    def update(self, dt):
        if self.paused:
            return
        self.time += dt
        for obj in self.objects:
            obj.update(dt, self.gravity, self.air_resistance)
        self.handle_collisions()

    def handle_collisions(self):
        for i, obj in enumerate(self.objects):
            if obj.position[1] <= 0:
                obj.position[1] = 0
                obj.velocity[1] = -obj.velocity[1] * obj.elasticity

            for other in self.objects[i+1:]:
                if np.linalg.norm(obj.position - other.position) < 1:
                    self.resolve_collision(obj, other)

            for obstacle in self.obstacles:
                if obstacle.collides_with(obj):
                    self.resolve_obstacle_collision(obj, obstacle)

    def resolve_collision(self, obj1, obj2):
        v1, v2 = obj1.velocity, obj2.velocity
        m1, m2 = obj1.mass, obj2.mass
        total_mass = m1 + m2
        obj1.velocity = v1 - 2*m2/total_mass * np.dot(v1-v2, obj1.position-obj2.position) / np.linalg.norm(obj1.position-obj2.position)**2 * (obj1.position-obj2.position)
        obj2.velocity = v2 - 2*m1/total_mass * np.dot(v2-v1, obj2.position-obj1.position) / np.linalg.norm(obj2.position-obj1.position)**2 * (obj2.position-obj1.position)
        
        obj1.velocity *= obj1.elasticity
        obj2.velocity *= obj2.elasticity

    def resolve_obstacle_collision(self, obj, obstacle):
        normal = np.sign(obj.position - obstacle.position)
        obj.velocity = obj.velocity - 2 * np.dot(obj.velocity, normal) * normal
        obj.velocity *= obj.elasticity
    
    def resolve_collision(self, obj1, obj2):
        v1, v2 = obj1.velocity, obj2.velocity
        m1, m2 = obj1.mass, obj2.mass
        total_mass = m1 + m2
        
        # Calculate new velocities
        new_v1 = v1 - 2*m2/total_mass * np.dot(v1-v2, obj1.position-obj2.position) / np.linalg.norm(obj1.position-obj2.position)**2 * (obj1.position-obj2.position)
        new_v2 = v2 - 2*m1/total_mass * np.dot(v2-v1, obj2.position-obj1.position) / np.linalg.norm(obj2.position-obj1.position)**2 * (obj2.position-obj1.position)
        
        # Apply elasticity
        obj1.velocity = v1 + (new_v1 - v1) * obj1.elasticity
        obj2.velocity = v2 + (new_v2 - v2) * obj2.elasticity

    def resolve_obstacle_collision(self, obj, obstacle):
        normal = np.sign(obj.position - obstacle.position)
        v_normal = np.dot(obj.velocity, normal) * normal
        v_tangent = obj.velocity - v_normal
        
        # Reflect the normal component and apply elasticity
        obj.velocity = v_tangent - v_normal * obj.elasticity
    
    def resolve_collision(self, obj1, obj2):
        v1, v2 = obj1.velocity, obj2.velocity
        m1, m2 = obj1.mass, obj2.mass
        total_mass = m1 + m2
        
        # Calculate new velocities
        new_v1 = v1 - 2*m2/total_mass * np.dot(v1-v2, obj1.position-obj2.position) / np.linalg.norm(obj1.position-obj2.position)**2 * (obj1.position-obj2.position)
        new_v2 = v2 - 2*m1/total_mass * np.dot(v2-v1, obj2.position-obj1.position) / np.linalg.norm(obj2.position-obj1.position)**2 * (obj2.position-obj1.position)
        
        # Apply elasticity
        obj1.velocity = v1 + (new_v1 - v1) * obj1.elasticity
        obj2.velocity = v2 + (new_v2 - v2) * obj2.elasticity

    def resolve_obstacle_collision(self, obj, obstacle):
        normal = np.sign(obj.position - obstacle.position)
        v_normal = np.dot(obj.velocity, normal) * normal
        v_tangent = obj.velocity - v_normal
        
        # Reflect the normal component and apply elasticity
        obj.velocity = v_tangent - v_normal * obj.elasticity

class Visualizer:
    def __init__(self, width, height):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.ui_manager = pygame_gui.UIManager((width, height))
        self.selected_object = None
        self.font = pygame.font.Font(None, 24)
        self.tracking_object = None
        self.sim = None  # We'll set this in the main function
        self.last_click_time = 0
        self.double_click_threshold = 0.3  # 300 milliseconds
        self.zoom_level = 1.0
        self.x_min, self.x_max = -10, 10
        self.y_min, self.y_max = 0, 20
        self.setup_ui()

    def setup_ui(self):
        self.spawn_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((10, 10), (100, 30)),
            text='Spawn Object',
            manager=self.ui_manager
        )
        self.add_obstacle_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((120, 10), (100, 30)),
            text='Add Obstacle',
            manager=self.ui_manager
        )
        self.pause_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((230, 10), (100, 30)),
            text='Pause',
            manager=self.ui_manager
        )
        self.gravity_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect((10, 50), (200, 20)),
            start_value=9.8,
            value_range=(0, 20),
            manager=self.ui_manager
        )
        self.air_resistance_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect((10, 80), (200, 20)),
            start_value=0.1,
            value_range=(0, 1),
            manager=self.ui_manager
        )
        self.zoom_in_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((340, 10), (50, 30)),
            text='+',
            manager=self.ui_manager
        )
        self.zoom_out_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((400, 10), (50, 30)),
            text='-',
            manager=self.ui_manager
        )

    def draw(self, sim):
        self.screen.fill((255, 255, 255))
        
        for obj in sim.objects:
            self.draw_object(obj)
            self.draw_trail(obj)

        for obstacle in sim.obstacles:
            self.draw_obstacle(obstacle)

        self.draw_info(sim)
        self.ui_manager.draw_ui(self.screen)
        pygame.display.flip()

        if self.tracking_object:
            self.center_on_tracked_object()

    def draw_object(self, obj):
        screen_x, screen_y = self.world_to_screen(obj.position)
        
        if obj == self.selected_object:
            pygame.draw.circle(self.screen, (255, 0, 0), (screen_x, screen_y), int(12 * self.zoom_level), 2)

        if obj == self.tracking_object:
            pygame.draw.circle(self.screen, (0, 255, 0), (screen_x, screen_y), int(14 * self.zoom_level), 2)

        if obj.shape == 'circle':
            pygame.draw.circle(self.screen, obj.color, (screen_x, screen_y), int(10 * self.zoom_level))
        elif obj.shape == 'square':
            size = int(20 * self.zoom_level)
            pygame.draw.rect(self.screen, obj.color, (screen_x - size//2, screen_y - size//2, size, size))

    def draw_obstacle(self, obstacle):
        screen_x, screen_y = self.world_to_screen(obstacle.position)
        width = int(obstacle.size[0] * 20 * self.zoom_level)
        height = int(obstacle.size[1] * 20 * self.zoom_level)
        pygame.draw.rect(self.screen, (100, 100, 100), 
                         (screen_x - width//2, screen_y - height//2, width, height))

    def draw_trail(self, obj):
        if len(obj.trail) > 1:
            points = [self.world_to_screen(pos) for pos in obj.trail]
            pygame.draw.lines(self.screen, obj.color, False, points, 2)

    def draw_info(self, sim):
        info_text = f"Time: {sim.time:.2f}s  Gravity: {sim.gravity:.2f}  Air Resistance: {sim.air_resistance:.2f}"
        info_surface = self.font.render(info_text, True, (0, 0, 0))
        self.screen.blit(info_surface, (10, self.height - 30))

        if self.selected_object:
            obj = self.selected_object
            obj_info = f"Mass: {obj.mass:.2f}  Pos: ({obj.position[0]:.2f}, {obj.position[1]:.2f})  Vel: ({obj.velocity[0]:.2f}, {obj.velocity[1]:.2f})"
            obj_surface = self.font.render(obj_info, True, (0, 0, 0))
            self.screen.blit(obj_surface, (10, self.height - 60))

    def handle_events(self, sim):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.handle_object_selection(sim, event.pos)
                elif event.button == 3:  # Right click
                    self.handle_obstacle_selection(sim, event.pos)
            
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.spawn_button:
                    self.spawn_object(sim)
                elif event.ui_element == self.add_obstacle_button:
                    self.open_obstacle_editor()
                elif event.ui_element == self.pause_button:
                    sim.paused = not sim.paused
                    self.pause_button.set_text('Resume' if sim.paused else 'Pause')
                elif event.ui_element == self.zoom_in_button:
                    self.zoom_level *= 1.1
                elif event.ui_element == self.zoom_out_button:
                    self.zoom_level /= 1.1

            if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                if event.ui_element == self.gravity_slider:
                    sim.gravity = event.value
                elif event.ui_element == self.air_resistance_slider:
                    sim.air_resistance = event.value
            
            self.ui_manager.process_events(event)
        
        return True

    def world_to_screen(self, position):
        x, y = position
        screen_x = int((x - self.x_min) / (self.x_max - self.x_min) * self.width * self.zoom_level)
        screen_y = int((self.y_max - y) / (self.y_max - self.y_min) * self.height * self.zoom_level)
        return screen_x, screen_y

    def spawn_object(self, sim):
        new_object = PhysicsObject(
            mass=1.0,
            position=[np.random.uniform(-5, 5), np.random.uniform(5, 15)],
            velocity=[np.random.uniform(-5, 5), np.random.uniform(-5, 5)],
            shape='circle'
        )
        sim.add_object(new_object)

    def open_obstacle_editor(self, obstacle=None):
        editor_dialog = ObstacleEditorDialog(
            self.ui_manager,
            pygame.Rect((self.width/2 - 150, self.height/2 - 125), (300, 250)),
            self,
            obstacle
        )

    def handle_object_selection(self, sim, mouse_pos):
        for obj in sim.objects:
            screen_x, screen_y = self.world_to_screen(obj.position)
            if np.linalg.norm(np.array([screen_x, screen_y]) - np.array(mouse_pos)) < 15 * self.zoom_level:
                self.selected_object = obj
                print(f"Object selected: {obj}")
                return
        self.selected_object = None
        print("No object selected")

    def handle_object_selection(self, sim, mouse_pos):
        current_time = time.time()
    
        for obj in sim.objects:
            screen_x, screen_y = self.world_to_screen(obj.position)
            if np.linalg.norm(np.array([screen_x, screen_y]) - np.array(mouse_pos)) < 15 * self.zoom_level:
                if obj == self.selected_object:
                    # Check for double-click
                    if current_time - self.last_click_time < self.double_click_threshold:
                        print(f"Double-click detected on object: {obj}")
                        self.open_object_menu()
                    else:
                        print(f"Single click on selected object: {obj}")
                else:
                    self.selected_object = obj
                    print(f"Object selected: {obj}")
                self.last_click_time = current_time
                return
    
        self.selected_object = None
        print("No object selected")

    def center_on_tracked_object(self):
        if self.tracking_object:
            x, y = self.tracking_object.position
            center_x = (self.x_min + self.x_max) / 2
            center_y = (self.y_min + self.y_max) / 2
            offset_x = x - center_x
            offset_y = y - center_y
            
            self.x_min += offset_x
            self.x_max += offset_x
            self.y_min += offset_y
            self.y_max += offset_y

    def open_object_menu(self):
        if self.selected_object:
            print(f"Opening menu for object: {self.selected_object}")
            menu_dialog = ObjectMenuDialog(
                self.ui_manager,
                pygame.Rect((self.width/2 - 200, self.height/2 - 150), (400, 300)),
                self
        )
        else:
            print("No object selected when trying to open menu")

class ObjectMenuDialog(UIWindow):
    def __init__(self, manager, rect, visualizer):
        super().__init__(rect, manager, window_display_title="Object Menu")
        
        self.visualizer = visualizer
        self.selected_object = visualizer.selected_object
        self.ui_manager = manager

        # Add custom buttons
        button_layout_rect = pygame.Rect(0, 0, 180, 30)
        self.edit_button = pygame_gui.elements.UIButton(
            relative_rect=button_layout_rect.move(10, 60),
            text="Edit Properties",
            container=self,
            manager=manager
        )
        self.delete_button = pygame_gui.elements.UIButton(
            relative_rect=button_layout_rect.move(10, 100),
            text="Delete Object",
            container=self,
            manager=manager
        )
        self.track_button = pygame_gui.elements.UIButton(
            relative_rect=button_layout_rect.move(10, 140),
            text="Track Object",
            container=self,
            manager=manager
        )

    def process_event(self, event):
        handled = super().process_event(event)
        
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.edit_button:
                self.open_edit_properties_dialog()
            elif event.ui_element == self.delete_button:
                self.delete_object()
            elif event.ui_element == self.track_button:
                self.toggle_tracking()
            handled = True

        return handled

    def open_edit_properties_dialog(self):
        if self.selected_object:
            edit_dialog = EditPropertiesDialog(
                self.ui_manager,
                pygame.Rect((self.rect.x + 50, self.rect.y + 50), (300, 250)),
                self.selected_object,
                self.visualizer
        )

    def delete_object(self):
        if self.selected_object:
            self.visualizer.sim.objects.remove(self.selected_object)
            self.visualizer.selected_object = None
            self.kill()

    def toggle_tracking(self):
        if self.selected_object:
            if self.visualizer.tracking_object == self.selected_object:
                self.visualizer.tracking_object = None
            else:
                self.visualizer.tracking_object = self.selected_object
            self.kill()

    def process_event(self, event):
        handled = super().process_event(event)
        
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.edit_button:
                self.open_edit_properties_dialog()
            elif event.ui_element == self.delete_button:
                self.delete_object()
            elif event.ui_element == self.track_button:
                self.toggle_tracking()
            handled = True

        return handled

    def open_edit_properties_dialog(self):
        if self.selected_object:
            edit_dialog = EditPropertiesDialog(self.ui_manager, pygame.Rect((self.rect.x + 50, self.rect.y + 50), (300, 250)), self.selected_object, self.visualizer)
            edit_dialog.set_blocking(True)

    def delete_object(self):
        if self.selected_object:
            self.visualizer.sim.objects.remove(self.selected_object)
            self.visualizer.selected_object = None
            self.kill()

    def toggle_tracking(self):
        if self.selected_object:
            if self.visualizer.tracking_object == self.selected_object:
                self.visualizer.tracking_object = None
            else:
                self.visualizer.tracking_object = self.selected_object
            self.kill()

class ObstacleEditorDialog(UIWindow):
    def __init__(self, manager, rect, visualizer, obstacle=None):
        super().__init__(rect, manager, window_display_title="Obstacle Editor")
        self.visualizer = visualizer
        self.obstacle = obstacle

        y_offset = 20
        self.x_entry = self.add_entry(manager, "X Position:", y_offset, str(obstacle.position[0]) if obstacle else "0")
        y_offset += 30
        self.y_entry = self.add_entry(manager, "Y Position:", y_offset, str(obstacle.position[1]) if obstacle else "0")
        y_offset += 30
        self.width_entry = self.add_entry(manager, "Width:", y_offset, str(obstacle.size[0]) if obstacle else "1")
        y_offset += 30
        self.height_entry = self.add_entry(manager, "Height:", y_offset, str(obstacle.size[1]) if obstacle else "1")
        
        self.save_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((10, y_offset + 30), (100, 30)),
            text="Save",
            container=self,
            manager=manager
        )

    def add_entry(self, manager, label, y_offset, default_value):
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, y_offset), (100, 20)),
            text=label,
            container=self,
            manager=manager
        )
        return pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((120, y_offset), (100, 20)),
            container=self,
            manager=manager,
            initial_text=default_value
        )

    def process_event(self, event):
        handled = super().process_event(event)
        
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.save_button:
                self.save_obstacle()
                handled = True

        return handled

    def save_obstacle(self):
        try:
            x = float(self.x_entry.get_text())
            y = float(self.y_entry.get_text())
            width = float(self.width_entry.get_text())
            height = float(self.height_entry.get_text())
            
            if self.obstacle:
                self.obstacle.position = np.array([x, y])
                self.obstacle.size = np.array([width, height])
            else:
                new_obstacle = Obstacle([x, y], [width, height])
                self.visualizer.sim.add_obstacle(new_obstacle)
            
            self.kill()
        except ValueError:
            error_dialog = pygame_gui.windows.UIMessageWindow(
                rect=pygame.Rect((self.rect.x + 50, self.rect.y + 50), (300, 150)),
                manager=self.ui_manager,
                window_title="Error",
                html_message="Invalid input. Please enter numeric values."
            )

class EditPropertiesDialog(UIWindow):
    def __init__(self, manager, rect, obj, visualizer):
        super().__init__(rect, manager, window_display_title="Edit Properties")
        self.obj = obj
        self.visualizer = visualizer
        self.ui_manager = manager

        y_offset = 20
        self.mass_entry = self.add_entry(manager, "Mass:", y_offset, str(obj.mass))
        y_offset += 30
        self.x_entry = self.add_entry(manager, "X Position:", y_offset, str(obj.position[0]))
        y_offset += 30
        self.y_entry = self.add_entry(manager, "Y Position:", y_offset, str(obj.position[1]))
        y_offset += 30
        self.vx_entry = self.add_entry(manager, "X Velocity:", y_offset, str(obj.velocity[0]))
        y_offset += 30
        self.vy_entry = self.add_entry(manager, "Y Velocity:", y_offset, str(obj.velocity[1]))
        y_offset += 30

        # Add elasticity slider
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, y_offset), (100, 20)),
            text="Elasticity:",
            container=self,
            manager=manager
        )
        self.elasticity_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect((120, y_offset), (150, 20)),
            start_value=obj.elasticity,
            value_range=(0, 1),
            container=self,
            manager=manager
        )
        y_offset += 30
        
        self.save_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((10, y_offset), (100, 30)),
            text="Save",
            container=self,
            manager=manager
        )

    def add_entry(self, manager, label, y_offset, default_value):
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, y_offset), (100, 20)),
            text=label,
            container=self,
            manager=manager
        )
        return pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((120, y_offset), (100, 20)),
            container=self,
            manager=manager,
            initial_text=default_value
        )

    def process_event(self, event):
        handled = super().process_event(event)
        
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.save_button:
                self.save_properties()
                handled = True

        return handled

    def save_properties(self):
        try:
            self.obj.mass = float(self.mass_entry.get_text())
            self.obj.position[0] = float(self.x_entry.get_text())
            self.obj.position[1] = float(self.y_entry.get_text())
            self.obj.velocity[0] = float(self.vx_entry.get_text())
            self.obj.velocity[1] = float(self.vy_entry.get_text())
            self.obj.elasticity = self.elasticity_slider.get_current_value()
            self.kill()
        except ValueError:
            error_dialog = pygame_gui.windows.UIMessageWindow(
                rect=pygame.Rect((self.rect.x + 50, self.rect.y + 50), (300, 150)),
                manager=self.ui_manager,
                window_title="Error",
                html_message="Invalid input. Please enter numeric values."
            )


def main():
    sim = Simulation()
    vis = Visualizer(800, 600)
    vis.sim = sim  # Set the simulation reference in the visualizer

    running = True
    while running:
        time_delta = vis.clock.tick(60) / 1000.0
        
        running = vis.handle_events(sim)
        
        sim.update(1/60)  # Update at 60 FPS
        vis.draw(sim)
        vis.ui_manager.update(time_delta)

    pygame.quit()

if __name__ == "__main__":
    main()