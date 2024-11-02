from manimlib import *

def add_axis_labels(scene, axes):
    axis_labels = label = Tex("xyz")
    if axes.z_axis.get_stroke_opacity() > 0:
        axis_labels.rotate(PI / 2, RIGHT)
        axis_labels[0].next_to(axes.x_axis.get_right(), OUT)
        axis_labels[1].next_to(axes.y_axis.get_top(), OUT)
        axis_labels[2].next_to(axes.z_axis.get_zenith(), RIGHT)
    else:
        axis_labels[1].clear_points()
        axis_labels[0].next_to(axes.x_axis.get_right(), UP)
        axis_labels[2].next_to(axes.y_axis.get_top(), RIGHT)

    scene.axis_labels = axis_labels
    scene.add(scene.axis_labels)

def get_default_wave_axes_and_plane(
    x_range=(0, 24),
    y_range=(-1, 1),
    z_range=(-1, 1),
    x_unit=1,
    y_unit=2,
    z_unit=2,
    origin_point=5 * LEFT,
    axes_opacity=0.5,
    plane_line_style=dict(
        stroke_color=GREY_C,
        stroke_width=1,
        stroke_opacity=0.5
    ),
):
    axes = ThreeDAxes(
        x_range=x_range,
        y_range=y_range,
        z_range=z_range,
        width=x_unit * (x_range[1] - x_range[0]),
        height=y_unit * (y_range[1] - y_range[0]),
        depth=z_unit * (z_range[1] - z_range[0]),
    )
    axes.shift(origin_point - axes.get_origin())
    axes.set_opacity(axes_opacity)
    axes.set_flat_stroke(False)
    plane = NumberPlane(
        axes.x_range, axes.y_range,
        width=axes.x_axis.get_length(),
        height=axes.y_axis.get_length(),
        background_line_style=plane_line_style,
        axis_config=dict(stroke_width=0),
    )
    plane.shift(axes.get_origin() - plane.get_origin())
    plane.set_flat_stroke(False)

    return axes, plane

