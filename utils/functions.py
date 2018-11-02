def get_points(x1, y1, x2, y2, point_num=10):
    points = []
    if x1 == x2 and y1 == y2:
        return points

    points.append((x1, y1))
    if x1 == x2:
        step = (y2 - y1) / point_num
        for i in range(1, point_num - 1):
            y = y1 + step * i
            points.append((x1, y))
    elif y1 == y2:
        step = (x2 - x1) / point_num
        for i in range(1, point_num - 1):
            x = x1 + step * i
            points.append((x, y1))
    else:
        step = (x2 - x1) / point_num
        k = (y2 - y1) / (x2 - x1)
        b = y1 - k * x1
        for i in range(1, point_num - 1):
            x = float("%.2f" % (x1 + i * step))
            y = float("%.2f" % (k * x + b))
            points.append((x, y))

    points.append((x2, y2))

    return points


if __name__ == '__main__':
    p = get_points(10, 34, 51, 60)
    print(len(p), p)
    print(list(range(1, 10)))
