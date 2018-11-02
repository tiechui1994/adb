import cv2


def show():
    image = cv2.imread("autojump.png", 3)
    cv2.imshow("i", image)
    cv2.waitKey()
    cv2.destroyAllWindows()


__ENV__ = {
    "A": 100
}


class _Env(object):
    @property
    def ENV(self):
        if not hasattr(_Env, '__ENV__'):
            self.reload()
            _Env.__ENV__ = __ENV__
        return getattr(_Env, '__ENV__')

    @staticmethod
    def reload():
        global __ENV__
        __ENV__["A"] = 200


Env = _Env()

if __name__ == '__main__':
    print(Env.ENV)
