class Interpolation:
    """
    This is a class that implements the Linear interpolation operation of one-dimensional and two-dimensional data
    """

    def __init__(self):
        pass

    @staticmethod
    def interpolate_1d(x, y, x_interp):
        """
        Linear interpolation of one-dimensional data
        :param x: The x-coordinate of the data point, list.
        :param y: The y-coordinate of the data point, list.
        :param x_interp: The x-coordinate of the interpolation point, list.
        :return: The y-coordinate of the interpolation point, list.
        >>> interpolation = Interpolation()
        >>> interpolation.interpolate_1d([1, 2, 3], [1, 2, 3], [1.5, 2.5])
        [1.5, 2.5]

        """

        # Calculate the slope and intercept for each segment
        slopes = [(y[i+1] - y[i]) / (x[i+1] - x[i]) for i in range(len(x)-1)]
        intercepts = [y[i] - slopes[i] * x[i] for i in range(len(x)-1)]

        # Interpolate for each segment
        interpolated_y = []
        for i in range(len(x_interp)):
            for j in range(len(x)-1):
                if x_interp[i] >= x[j] and x_interp[i] <= x[j+1]:
                    interpolated_y.append(slopes[j] * x_interp[i] + intercepts[j])
                    break

        return interpolated_y

    @staticmethod
    def interpolate_2d(x, y, z, x_interp, y_interp):
        """
        Linear interpolation of two-dimensional data
        :param x: The x-coordinate of the data point, list.
        :param y: The y-coordinate of the data point, list.
        :param z: The z-coordinate of the data point, list.
        :param x_interp: The x-coordinate of the interpolation point, list.
        :param y_interp: The y-coordinate of the interpolation point, list.
        :return: The z-coordinate of the interpolation point, list.
        >>> interpolation = Interpolation()
        >>> interpolation.interpolate_2d([1, 2, 3], [1, 2, 3], [[1, 2, 3], [4, 5, 6], [7, 8, 9]], [1.5, 2.5], [1.5, 2.5])
        [3.0, 7.0]

        """

        # Calculate the slope and intercept for each segment
        slopes_x = [(z[i+1][j] - z[i][j]) / (x[i+1] - x[i]) for i in range(len(x)-1) for j in range(len(y))]
        intercepts_x = [z[i][j] - slopes_x[i] * x[i] for i in range(len(x)-1) for j in range(len(y))]

        slopes_y = [(z[i][j+1] - z[i][j]) / (y[j+1] - y[j]) for i in range(len(x)-1) for j in range(len(y)-1)]
        intercepts_y = [z[i][j] - slopes_y[i] * y[j] for i in range(len(x)-1) for j in range(len(y)-1)]

        # Interpolate for each segment
        interpolated_z = []
        for i in range(len(x_interp)):
            for j in range(len(y_interp)):
                for k in range(len(x)-1):
                    for l in range(len(y)-1):
                        if x_interp[i] >= x[k] and x_interp[i] <= x[k+1] and y_interp[j] >= y[l] and y_interp[j] <= y[l+1]:
                            interpolated_z.append(slopes_x[k*l] * x_interp[i] + intercepts_x[k*l] + slopes_y[k][l+1] * y_interp[j] + intercepts_y[k][l+1])
                            break

        return interpolated_z