import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from itertools import combinations

def main():
    # Example usage
    cube = create_cube(size=1, center=(0, 0, 0), num_points_per_edge=2)
    print(cube)
    print(f"Shape of the cube array: {cube.shape}")

def create_cube(size=1, center=(0, 0, 0), num_points_per_edge=2):
    """
    Create a cube represented by an array of x, y, z coordinates.
    
    Parameters:
    - size: The length of each side of the cube (default: 1)
    - center: The (x, y, z) coordinates of the cube's center (default: (0, 0, 0))
    - num_points_per_edge: Number of points to generate along each edge (default: 2)
    
    Returns:
    - numpy array of shape (num_points, 3) representing the cube's vertices
    """
    
    # Generate points along each dimension
    points = np.linspace(-size/2, size/2, num_points_per_edge)
    
    # Create meshgrid
    x, y, z = np.meshgrid(points, points, points)
    
    # Reshape and stack coordinates
    cube_coords = np.vstack((x.ravel(), y.ravel(), z.ravel())).T
    
    # Translate cube to specified center
    cube_coords += np.array(center)
    
    return cube_coords


def translate_cube(cube, translation):
    """
    Translate the cube by a given vector.
    
    Parameters:
    - cube: numpy array of shape (num_points, 3) representing the cube's vertices
    - translation: list or numpy array of shape (3,) representing the translation vector [dx, dy, dz]
    
    Returns:
    - numpy array of shape (num_points, 3) representing the translated cube's vertices
    """
    return cube + np.array(translation)

def rotate_cube(cube, angles):
    """
    Rotate the cube around the x, y, and z axes.
    
    Parameters:
    - cube: numpy array of shape (num_points, 3) representing the cube's vertices
    - angles: list or numpy array of shape (3,) representing rotation angles [theta_x, theta_y, theta_z] in radians
    
    Returns:
    - numpy array of shape (num_points, 3) representing the rotated cube's vertices
    """
    theta_x, theta_y, theta_z = angles
    
    # Rotation matrices
    Rx = np.array([[1, 0, 0],
                   [0, np.cos(theta_x), -np.sin(theta_x)],
                   [0, np.sin(theta_x), np.cos(theta_x)]])
    
    Ry = np.array([[np.cos(theta_y), 0, np.sin(theta_y)],
                   [0, 1, 0],
                   [-np.sin(theta_y), 0, np.cos(theta_y)]])
    
    Rz = np.array([[np.cos(theta_z), -np.sin(theta_z), 0],
                   [np.sin(theta_z), np.cos(theta_z), 0],
                   [0, 0, 1]])
    
    # Combined rotation matrix
    R = Rz @ Ry @ Rx
    
    # Apply rotation
    return cube @ R.T

def visualize_cube(cube, title="Cube Visualization"):
    """
    Visualize the cube in 3D.
    
    Parameters:
    - cube: numpy array of shape (num_points, 3) representing the cube's vertices
    - title: string, the title of the plot
    """
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Plot vertices
    ax.scatter(cube[:, 0], cube[:, 1], cube[:, 2], c='r', s=50)
    
    # Determine edges
    edges = []
    for i, j in combinations(range(len(cube)), 2):
        if np.sum(np.abs(cube[i] - cube[j]) > 1e-6) == 1:  # Only one coordinate differs
            edges.append((i, j))
    
    # Plot edges
    for edge in edges:
        ax.plot([cube[edge[0], 0], cube[edge[1], 0]],
                [cube[edge[0], 1], cube[edge[1], 1]],
                [cube[edge[0], 2], cube[edge[1], 2]], 'b')
    
    # Set labels and title
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title(title)
    
    # Set aspect ratio to 'equal'
    ax.set_box_aspect((np.ptp(cube[:, 0]), np.ptp(cube[:, 1]), np.ptp(cube[:, 2])))
    
    plt.show()

def visualize_cube_1(cube, title="Cube Visualization"):
    """
    Visualize the cube in 3D.
    
    Parameters:
    - cube: numpy array of shape (num_points, 3) representing the cube's vertices
    - title: string, the title of the plot
    """
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Plot vertices
    ax.scatter(cube[:, 0], cube[:, 1], cube[:, 2], c='r', s=50)
    
    # Define edges
    edges = [
        (0, 1), (0, 2), (0, 4), (1, 3), (1, 5), (2, 3),
        (2, 6), (3, 7), (4, 5), (4, 6), (5, 7), (6, 7)
    ]
    
    # Plot edges
    for edge in edges:
        ax.plot([cube[edge[0], 0], cube[edge[1], 0]],
                [cube[edge[0], 1], cube[edge[1], 1]],
                [cube[edge[0], 2], cube[edge[1], 2]], 'b')
    
    # Set labels and title
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title(title)
    
    # Set aspect ratio to 'equal'
    ax.set_box_aspect((np.ptp(cube[:, 0]), np.ptp(cube[:, 1]), np.ptp(cube[:, 2])))
    
    plt.show()
