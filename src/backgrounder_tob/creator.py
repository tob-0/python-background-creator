from uuid import uuid4
from PIL import Image, ImageFilter
import re
from typing import NoReturn, Optional
from pathlib import Path


class Creator:
    def __init__(
        self,
        aspect_ratio: str = "4/5",
        orientation: str = "vertical",
        img: Optional[str] = None,
        output_dir: str = "./",
        verbose: bool = False,
    ) -> NoReturn:
        """Create an object for background creation with a specific aspect ratio.

        Args:
            aspect_ratio (str, optional): Aspect ratio of the background. Defaults to "4/5".
            orientation (str, optional): Orientation of the source picture, "vertical" or "horizontal". Defaults to "vertical".
            img (_type_, optional): PIL.Image object to initialize with. Defaults to None.
        """
        self.orientation: str = orientation
        self.ratio: float = self.__parse_aspect_ratio(aspect_ratio)
        self.img = img
        self.output_dir: str = output_dir
        self.verbose: bool = verbose

    def __parse_aspect_ratio(self, aspect_ratio_str: str) -> float:
        ratio = 1.0
        try:
            decimal_aspect_ratio = float(aspect_ratio_str)
            if 0 < decimal_aspect_ratio < 1:
                ratio = decimal_aspect_ratio

        except ValueError:
            result = re.search(r"(\d+)[:/-|]{1}(\d+)", aspect_ratio_str)
            if result:
                aspect_ratio_dimensions = list(
                    map(lambda dim: int(dim), result.groups())
                )
                if len(aspect_ratio_dimensions) == 2:
                    if aspect_ratio_dimensions[0] > aspect_ratio_dimensions[1]:
                        self.orientation = "horizontal"
                    else:
                        self.orientation = "vertical"

                    if self.orientation == "vertical":
                        ratio = aspect_ratio_dimensions[0] / aspect_ratio_dimensions[1]
                    elif self.orientation == "horizontal":
                        ratio = aspect_ratio_dimensions[1] / aspect_ratio_dimensions[0]

        return ratio

    def _blrd_bg(self, img: Image = None, blur_ratio: Optional[float] = None) -> Image:
        img = img or self.img
        src_w, src_h = img.size
        bg_w = int(src_h * self.ratio)
        blur_ratio = bg_w // 5 or blur_ratio

        bg = img.copy()
        rsz_value = (bg_w, src_h)
        bg = bg.resize(rsz_value)
        bg = bg.filter(ImageFilter.GaussianBlur(blur_ratio))
        offset = (bg_w - src_w) // 2
        bg.paste(img, (offset, 0))
        return bg

    def _clrd_bg(
        self, img: Image = None, color: Optional[tuple[int]] = (0, 0, 0)
    ) -> Image:
        img = img or self.img
        src_w, src_h = img.size
        bg_w = int(src_h * self.ratio)
        bg = Image.new("RGB", (bg_w, src_h), color)
        offset = (bg_w - src_w) // 2
        bg.paste(img, (offset, 0))
        return bg

    def _brtst_c_bg(
        self, img: Image = None, threshold: int = 150, threshold_count: int = 3
    ) -> Image:
        img = img or self.img
        rgb_img = img.convert("RGB")
        src_w, src_h = img.size
        bg_w = int(src_h * self.ratio)
        brightest_color = (0, 0, 0)
        highest_brightness = 0
        for w in [0, src_w - 1]:
            for h in range(src_h // 2):
                r, g, b = rgb_img.getpixel((w, h))
                if len([c for c in (r, g, b) if c > threshold]) >= threshold_count:
                    continue
                perceived_brightness = 0.2126 * r + 0.7152 * g + 0.0722 * b
                if perceived_brightness >= highest_brightness:
                    highest_brightness = perceived_brightness
                    brightest_color = (r, g, b)

        bg = Image.new("RGB", (bg_w, src_h), brightest_color)
        offset = (bg_w - src_w) // 2
        bg.paste(img, (offset, 0))
        return bg

    def _drkst_c_bg(self, img: Image = None) -> Image:
        img = img or self.img
        rgb_img = img.convert("RGB")
        src_w, src_h = img.size
        bg_w = int(src_h * self.ratio)
        darkest_color = (255, 255, 255)
        highest_brightness = 100
        for w in [0, src_w - 1]:
            for h in range(src_h):
                r, g, b = rgb_img.getpixel((w, h))
                perceived_brightness = 0.2126 * r + 0.7152 * g + 0.0722 * b
                if perceived_brightness <= highest_brightness:
                    highest_brightness = perceived_brightness
                    brightest_color = (r, g, b)

        bg = Image.new("RGB", (bg_w, src_h), brightest_color)
        offset = (bg_w - src_w) // 2
        bg.paste(img, (offset, 0))
        return bg

    def generate(
        self,
        img=None,
        background_type: Optional[str] = "BLURRED",
        save: Optional[bool] = False,
        save_folder: Optional[str] = None,
        show: Optional[bool] = False,
        *args,
        **kwargs
    ):

        try:
            img = img or self.img
            save_folder = save_folder or self.output_dir
            if save_folder[-1] != "/":
                save_folder += "/"
            save_path = None

            if type(img) == str:
                img = Image.open(img)
            elif type(img) == Image:
                raise ValueError('"img" should be either a str or PIL.Image')
            if save:
                save_path = (
                    save_folder + str(uuid4()) + "." + img.filename.split(".")[-1]
                )
                Path(save_folder).mkdir(exist_ok=True, parents=True)

            if background_type == "WHITE":
                kwargs["color"] = (255, 255, 255)
            elif background_type == "BLACK":
                kwargs["color"] = (0, 0, 0)

            backgrounded_image = {
                "BLURRED": self._blrd_bg,
                "BLACK": self._clrd_bg,
                "WHITE": self._clrd_bg,
                "BRIGHTEST": self._brtst_c_bg,
                "DARKEST": self._drkst_c_bg,
                "COLOR": self._clrd_bg,
            }[background_type](img, *args, **kwargs)
            if save:
                backgrounded_image.save(save_path, quality=95)

            if show:
                backgrounded_image.show()
        except Exception as e:
            print("Error during generation: %s" % e)
