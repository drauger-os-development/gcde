/**
 * Author: Jason White
 *
 * Description:
 * Reads joystick/gamepad events and displays them.
 *
 * Compile:
 * gcc joystick.c -o joystick
 *
 * Run:
 * ./joystick [/dev/input/jsX]
 *
 * See also:
 * https://www.kernel.org/doc/Documentation/input/joystick-api.txt
 *
 * Modified by: Thomas Castleman <contact@draugeros.org>
 *
 *
 * Modifications:
 *  * Removed button support
 *  * Added directional understanding for left joystick
 */
#include <fcntl.h>
#include <iostream>
#include <unistd.h>
#include <linux/joystick.h>
#include <string>
#include <cmath>

using namespace std;

#define elif else if
/**
 * Reads a joystick event from the joystick device.
 *
 * Returns 0 on success. Otherwise -1 is returned.
 */
int read_event(int fd, struct js_event *event)
{
    ssize_t bytes;

    bytes = read(fd, event, sizeof(*event));

    if (bytes == sizeof(*event))
        return 0;

    /* Error, could not read full event. */
    return -1;
}

/**
 * Returns the number of axes on the controller or 0 if an error occurs.
 */
size_t get_axis_count(int fd)
{
    __u8 axes;

    if (ioctl(fd, JSIOCGAXES, &axes) == -1)
        return 0;

    return axes;
}

/**
 * Returns the number of buttons on the controller or 0 if an error occurs.
 */
size_t get_button_count(int fd)
{
    __u8 buttons;
    if (ioctl(fd, JSIOCGBUTTONS, &buttons) == -1)
        return 0;

    return buttons;
}

/**
 * Current state of an axis.
 */
struct axis_state {
    short x, y;
};

/**
 * Keeps track of the current axis state.
 *
 * NOTE: This function assumes that axes are numbered starting from 0, and that
 * the X axis is an even number, and the Y axis is an odd number. However, this
 * is usually a safe assumption.
 *
 * Returns the axis that the event indicated.
 */
size_t get_axis_state(struct js_event *event, struct axis_state axes[3])
{
    size_t axis = event->number / 2;

    if (axis < 3)
    {
        if (event->number % 2 == 0)
            axes[axis].x = event->value;
        else
            axes[axis].y = event->value;
    }

    return axis;
}

// Get the angle at which the joystick is pointing,
// And how far
string get_direction(struct axis_state axis[0])
{
    //Get hypotenuse, this will determine how far we are from center
    //THAT tells us whether we are in the dead-zone or not
    double x = axis->x;
    double y = axis->y * -1;
    //double z = pow((pow(x, 2) + pow(y, 2)), 0.5);
    if (pow((pow(x, 2) + pow(y, 2)), 0.5) > 3000)
    {
        // If Y > X, we go left or up
        if (y > x)
        {
            if (y > -x)
            {
                return "UP";
            }
            else
            {
                return "LEFT";
            }
        }
        // If X > Y, we go right or down
        elif (x > y)
        {
            if (x > -y)
            {
                return "RIGHT";
            }
            else
            {
                return "DOWN";
            }
            // return "RIGHT or DOWN!";
        }
        else
        {
            return "None";
        }
    }
    else
    {
        return "None";
    }
}


int main(int argc, char *argv[])
{
    const char *device;
    int js;
    struct js_event event;
    struct axis_state axes[3] = {0};
    size_t axis;
    string direction;

    if (argc > 1)
        device = argv[1];
    else
        device = "/dev/input/js0";

    js = open(device, O_RDONLY);

    if (js == -1)
        perror("Could not open joystick");

    /* This loop will exit if the controller is unplugged. */
    while (read_event(js, &event) == 0)
    {
        switch (event.type)
        {
            case JS_EVENT_AXIS:
                axis = get_axis_state(&event, axes);
                if (axis == 0)
                    direction = get_direction(axes);
                    if (direction != "")
                    {
                        cout << direction << endl;
                    }
                break;
            default:
                /* Ignore init events. */
                break;
        }

        //fflush(stdout);
        //usleep(500);
    }

    close(js);
    return 0;
}
