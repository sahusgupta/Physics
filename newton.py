import pygame
import pygame_gui
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import random
import cProfile
import pstats

class PhysicsObject:
    def __init__(self, mass, position, velocity, acceleration, shape='circle', color=None, elasticity=0.8):
        self.mass = mass
        self.position = np.array(position, dtype=float)
        self.velocity = np.array(velocity, dtype=float)
        self.acceleration = np.array(acceleration, dtype=float)
        self.shape = shape
        self.color = color or (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.elasticity = elasticity
        self.trail = []
        self.initial_position = np.array(position, dtype=float)
        self.work_done = 0

    def update(self, dt, gravity, air_resistance):
        old_velocity = self.velocity.copy()
        self.acceleration[1] -= gravity
        self.acceleration -= air_resistance * self.velocity
        self.velocity += self.acceleration * dt
        self.position += self.velocity * dt
        self.trail.append(self.position.copy())
        if len(self.trail) > 100:
            self.trail.pop(0)
        
        force = self.mass * (self.velocity - old_velocity) / dt
        displacement = self.velocity * dt
        self.work_done += np.dot(force, displacement)

    @property
    def kinetic_energy(self):
        return 0.5 * self.mass * np.sum(self.velocity**2)

    @property
    def momentum(self):
        return self.mass * self.velocity

    @property
    def gravitational_potential_energy(self):
        return self.mass * Simulation.gravity * (self.position[1] - self.initial_position[1])

class Obstacle:
    def __init__(self, position, size):
        self.position = np.array(position)
        self.size = np.array(size)

    def collides_with(self, obj):
        return np.all(np.abs(obj.position - self.position) < (self.size + 1) / 2)

class Simulation:
    gravity = 9.8
    air_resistance = 0.1

    def __init__(self):
        self.objects = []
        self.obstacles = []
        self.time = 0

    def add_object(self, obj):
        self.objects.append(obj)

    def add_obstacle(self, obstacle):
        self.obstacles.append(obstacle)

    def update(self, dt):
        self.time += dt
        for obj in self.objects:
            obj.update(dt, self.gravity, self.air_resistance)
        self.handle_collisions()

    def handle_collisions(self):
        for obj in self.objects:
            if obj.position[1] <= 0:
                obj.position[1] = 0
                obj.velocity[1] = -obj.velocity[1] * obj.elasticity

            for other in self.objects:
                if obj != other and np.linalg.norm(obj.position - other.position) < 1:
                    self.resolve_collision(obj, other)

            for obstacle in self.obstacles:
                if obstacle.collides_with(obj):
                    self.resolve_obstacle_collision(obj, obstacle)

    def resolve_collision(self, obj1, obj2):
        v1, v2 = obj1.velocity, obj2.velocity
        m1, m2 = obj1.mass, obj2.mass
        obj1.velocity = v1 - 2*m2/(m1+m2) * np.dot(v1-v2, obj1.position-obj2.position) / np.linalg.norm(obj1.position-obj2.position)**2 * (obj1.position-obj2.position)
        obj2.velocity = v2 - 2*m1/(m1+m2) * np.dot(v2-v1, obj2.position-obj1.position) / np.linalg.norm(obj2.position-obj1.position)**2 * (obj2.position-obj1.position)
        
        obj1.velocity *= obj1.elasticity
        obj2.velocity *= obj2.elasticity

    def resolve_obstacle_collision(self, obj, obstacle):
        normal = np.sign(obj.position - obstacle.position)
        obj.velocity = obj.velocity - 2 * np.dot(obj.velocity, normal) * normal
        obj.velocity *= obj.elasticity

class Visualizer:
    def __init__(self, width, height):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.fig, self.ax = plt.subplots(figsize=(5, 5))
        self.ui_manager = pygame_gui.UIManager((width, height))
        self.setup_ui()
        self.locked_object = None
        self.object_dialog = None
        self.obstacle_dialog = None
        self.selected_object = None

    def setup_ui(self):
        self.spawn_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (100, 50)), text='Spawn Object', manager=self.ui_manager)
        self.add_obstacle_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((120, 10), (100, 50)), text='Add Obstacle', manager=self.ui_manager)
        self.gravity_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((10, 70), (200, 20)), start_value=Simulation.gravity, value_range=(0, 20), manager=self.ui_manager)
        self.gravity_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((220, 70), (100, 20)), text=f'Gravity: {Simulation.gravity:.2f}', manager=self.ui_manager)
        self.air_resistance_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((10, 100), (200, 20)), start_value=Simulation.air_resistance, value_range=(0, 1), manager=self.ui_manager)
        self.air_resistance_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((220, 100), (150, 20)), text=f'Air Resistance: {Simulation.air_resistance:.2f}', manager=self.ui_manager)
        self.object_properties = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((10, 130), (300, 200)), html_text="Select an object to view properties", manager=self.ui_manager)

    def draw(self, sim):
        self.screen.fill((255, 255, 255))
        
        for obj in sim.objects:
            self.draw_object(obj)
            self.draw_trail(obj)

        for obstacle in sim.obstacles:
            pygame.draw.rect(self.screen, (100, 100, 100), 
                             (obstacle.position[0] - obstacle.size[0]/2, 
                              self.height - obstacle.position[1] - obstacle.size[1]/2, 
                              obstacle.size[0], obstacle.size[1]))

        self.update_plot(sim)
        self.ui_manager.draw_ui(self.screen)
        pygame.display.flip()

    def draw_object(self, obj):
        x, y = obj.position
        screen_x, screen_y = int(x * 50 + self.width/2), int(self.height - y * 50)
        
        if obj == self.selected_object:
            pygame.draw.circle(self.screen, (255, 0, 0), (screen_x, screen_y), 15, 2)

        if obj.shape == 'circle':
            pygame.draw.circle(self.screen, obj.color, (screen_x, screen_y), 10)
        elif obj.shape == 'square':
            pygame.draw.rect(self.screen, obj.color, (screen_x-10, screen_y-10, 20, 20))
        elif obj.shape == 'triangle':
            points = [(screen_x, screen_y-10), (screen_x-10, screen_y+10), (screen_x+10, screen_y+10)]
            pygame.draw.polygon(self.screen, obj.color, points)
        elif obj.shape == 'arrow':
            pygame.draw.line(self.screen, obj.color, (screen_x-10, screen_y), (screen_x+10, screen_y), 5)
            pygame.draw.polygon(self.screen, obj.color, [(screen_x+10, screen_y), (screen_x, screen_y-5), (screen_x, screen_y+5)])

    def draw_trail(self, obj):
        if len(obj.trail) > 1:
            points = [(int(x * 50 + self.width/2), int(self.height - y * 50)) for x, y in obj.trail]
            pygame.draw.lines(self.screen, obj.color, False, points, 2)

    def update_plot(self, sim):
        self.ax.clear()
        for obj in sim.objects:
            self.ax.plot(obj.position[0], obj.position[1], 'o', color=tuple(c/255 for c in obj.color))
        for obstacle in sim.obstacles:
            rect = plt.Rectangle((obstacle.position[0] - obstacle.size[0]/2, obstacle.position[1] - obstacle.size[1]/2), 
                                 obstacle.size[0], obstacle.size[1], fill=True, color='gray')
            self.ax.add_patch(rect)
            
        if self.locked_object:
            self.ax.set_xlim(self.locked_object.position[0] - 5, self.locked_object.position[0] + 5)
            self.ax.set_ylim(self.locked_object.position[1] - 5, self.locked_object.position[1] + 5)
        else:
            self.ax.set_xlim(-10, 10)
            self.ax.set_ylim(0, 20)
        
        self.ax.set_title(f"Time: {sim.time:.2f}s")
        self.ax.axhline(y=0, color='k', linestyle='-', linewidth=2)

        canvas = FigureCanvasAgg(self.fig)
        canvas.draw()
        renderer = canvas.get_renderer()
        raw_data = renderer.buffer_rgba()
        size = canvas.get_width_height()
        surf = pygame.image.frombuffer(raw_data, size, "RGBA")
        self.screen.blit(surf, (self.width - size[0], 0))

    def handle_events(self, sim):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_object_selection(sim, event.pos)
            
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.spawn_button:
                    self.open_object_dialog()
                elif event.ui_element == self.add_obstacle_button:
                    self.open_obstacle_dialog()
            
            if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                if event.ui_element == self.gravity_slider:
                    Simulation.gravity = event.value
                    self.gravity_label.set_text(f'Gravity: {Simulation.gravity:.2f}')
                elif event.ui_element == self.air_resistance_slider:
                    Simulation.air_resistance = event.value
                    self.air_resistance_label.set_text(f'Air Resistance: {Simulation.air_resistance:.2f}')

            if self.object_dialog:
                dialog_action = self.object_dialog.handle_event(event)
                if dialog_action:
                    self.spawn_object_from_dialog(sim, dialog_action)
                    self.object_dialog = None

            if self.obstacle_dialog:
                dialog_action = self.obstacle_dialog.handle_event(event)
                if dialog_action:
                    self.add_obstacle_from_dialog(sim, dialog_action)
                    self.obstacle_dialog = None
            
            self.ui_manager.process_events(event)
        
        self.update_object_properties()
        return True

    def handle_object_selection(self, sim, mouse_pos):
        for obj in sim.objects:
            screen_x = int(obj.position[0] * 50 + self.width/2)
            screen_y = int(self.height - obj.position[1] * 50)
            if np.linalg.norm(np.array([screen_x, screen_y]) - np.array(mouse_pos)) < 15:
                self.selected_object = obj
                return
        self.selected_object = None

    def open_object_dialog(self):
        self.object_dialog = ObjectCustomizationDialog(self.ui_manager, pygame.Rect((300, 50), (400, 300)))

    def open_obstacle_dialog(self):
        self.obstacle_dialog = ObstacleCustomizationDialog(self.ui_manager, pygame.Rect((300, 50), (400, 200)))

    def spawn_object_from_dialog(self, sim, object_properties):
        new_object = PhysicsObject(
            mass=object_properties['mass'],
            position=[object_properties['x'], object_properties['y']],
            velocity=[object_properties['vx'], object_properties['vy']],
            acceleration=[0, 0],
            shape=object_properties['shape'],
            elasticity=object_properties['elasticity']
        )
        sim.add_object(new_object)

    def add_obstacle_from_dialog(self, sim, obstacle_properties):
        new_obstacle = Obstacle(
            position=[obstacle_properties['x'], obstacle_properties['y']],
            size=[obstacle_properties['width'], obstacle_properties['height']]
        )
        sim.add_obstacle(new_obstacle)

    def update_object_properties(self):
        if self.selected_object:
            properties = f"""
            Mass: {self.selected_object.mass:.2f}
            Position: ({self.selected_object.position[0]:.2f}, {self.selected_object.position[1]:.2f})
            Velocity: ({self.selected_object.velocity[0]:.2f}, {self.selected_object.velocity[1]:.2f})
            Acceleration: ({self.selected_object.acceleration[0]:.2f}, {self.selected_object.acceleration[1]:.2f})
            Kinetic Energy: {self.selected_object.kinetic_energy:.2f}
            Potential Energy: {self.selected_object.gravitational_potential_energy:.2f}
            Momentum: ({self.selected_object.momentum[0]:.2f}, {self.selected_object.momentum[1]:.2f})
            Work Done: {self.selected_object.work_done:.2f}
            """
            self.object_properties.html_text = properties
            self.object_properties.rebuild()

class ObjectCustomizationDialog:
    def __init__(self, ui_manager, rect):
        self.window = pygame_gui.elements.UIWindow(rect, ui_manager, "Spawn Object")
        
        y_offset = 10
        self.mass_entry = self.add_number_entry(ui_manager, "Mass:", y_offset, 1.0)
        y_offset += 30
        self.x_entry = self.add_number_entry(ui_manager, "X Position:", y_offset, 0.0)
        y_offset += 30
        self.y_entry = self.add_number_entry(ui_manager, "Y Position:", y_offset, 10.0)
        y_offset += 30
        self.vx_entry = self.add_number_entry(ui_manager, "X Velocity:", y_offset, 0.0)
        y_offset += 30
        self.vy_entry = self.add_number_entry(ui_manager, "Y Velocity:", y_offset, 0.0)
        y_offset += 30
        self.elasticity_entry = self.add_number_entry(ui_manager, "Elasticity:", y_offset, 0.8)
        y_offset += 30
        
        self.shape_dropdown = pygame_gui.elements.UIDropDownMenu(
            ["circle", "square", "triangle", "arrow"],
            "circle",
            pygame.Rect((10, y_offset), (180, 30)),
            ui_manager,
            container=self.window
        )
        
        self.confirm_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((10, 250), (100, 30)),
            text="Confirm",
            manager=ui_manager,
            container=self.window
        )

    def add_number_entry(self, ui_manager, label, y_offset, default_value):
        pygame_gui.elements.UILabel(
            pygame.Rect((10, y_offset), (100, 20)),
            label,
            ui_manager,
            container=self.window
        )
        return pygame_gui.elements.UITextEntryLine(
            pygame.Rect((120, y_offset), (100, 20)),
            ui_manager,
            container=self.window,
            initial_text=str(default_value)
        )

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.confirm_button:
                return self.get_object_properties()
        return None

    def get_object_properties(self):
        return {
            'mass': float(self.mass_entry.get_text()),
            'x': float(self.x_entry.get_text()),
            'y': float(self.y_entry.get_text()),
            'vx': float(self.vx_entry.get_text()),
            'vy': float(self.vy_entry.get_text()),
            'elasticity': float(self.elasticity_entry.get_text()),
            'shape': self.shape_dropdown.selected_option
        }

class ObstacleCustomizationDialog:
    def __init__(self, ui_manager, rect):
        self.window = pygame_gui.elements.UIWindow(rect, ui_manager, "Add Obstacle")
        
        y_offset = 10
        self.x_entry = self.add_number_entry(ui_manager, "X Position:", y_offset, 0.0)
        y_offset += 30
        self.y_entry = self.add_number_entry(ui_manager, "Y Position:", y_offset, 5.0)
        y_offset += 30
        self.width_entry = self.add_number_entry(ui_manager, "Width:", y_offset, 2.0)
        y_offset += 30
        self.height_entry = self.add_number_entry(ui_manager, "Height:", y_offset, 1.0)
        y_offset += 30
        
        self.confirm_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((10, y_offset), (100, 30)),
            text="Confirm",
            manager=ui_manager,
            container=self.window
        )

    def add_number_entry(self, ui_manager, label, y_offset, default_value):
        pygame_gui.elements.UILabel(
            pygame.Rect((10, y_offset), (100, 20)),
            label,
            ui_manager,
            container=self.window
        )
        return pygame_gui.elements.UITextEntryLine(
            pygame.Rect((120, y_offset), (100, 20)),
            ui_manager,
            container=self.window,
            initial_text=str(default_value)
        )

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.confirm_button:
                return self.get_obstacle_properties()
        return None

    def get_obstacle_properties(self):
        return {
            'x': float(self.x_entry.get_text()),
            'y': float(self.y_entry.get_text()),
            'width': float(self.width_entry.get_text()),
            'height': float(self.height_entry.get_text())
        }

def main():
    sim = Simulation()
    vis = Visualizer(1200, 800)

    profiler = cProfile.Profile()
    profiler.enable()

    running = True
    while running:
        time_delta = vis.clock.tick(60) / 1000.0
        
        running = vis.handle_events(sim)
        
        sim.update(1/60)  # Update at 60 FPS
        vis.draw(sim)
        vis.ui_manager.update(time_delta)

    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats('cumulative')
    stats.print_stats()

    pygame.quit()

if __name__ == "__main__":
    main()