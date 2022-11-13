from pygame import Surface, image


class PygameTools:
    @classmethod
    def font_surface(cls, font_obj, text, color, bg_color=None, is_anti: bool = True) -> tuple:
        """
        pygame文本处理
        :param font_obj: pygame font Object
        :param text: 内容
        :param color: 颜色
        :param bg_color: 背景色(None透明)
        :param is_anti: 是否抗锯齿
        :return: (SurfaceObject, SurfaceSize, SurfaceRect)
        """
        surface: Surface = font_obj.render(text, is_anti, color, bg_color)
        return surface, surface.get_size(), surface.get_rect()

    @classmethod
    def load_image(cls, filename):
        try:
            return True, image.load(filename)
        except Exception as e:
            return False, e
