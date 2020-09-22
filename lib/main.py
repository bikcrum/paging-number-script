from PIL import Image, ImageDraw, ImageFont
import os
import sys


class Pager:
    def __init__(self, bg_color='white',
                 text_color='white',
                 text_size=20,
                 font_file=None,
                 padding=20,
                 min_height=0,
                 min_width=0,
                 start_page=1,
                 page_format='%d'):

        self.bg_color = bg_color
        self.text_color = text_color
        self.text_size = text_size
        self.padding = padding
        self.min_height = min_height
        self.min_width = min_width
        self.start_page = start_page
        self.page_format = page_format

        if font_file is None:
            self.font = ImageFont.load_default()
        else:
            self.font = ImageFont.truetype(font_file, self.text_size)

    def _get_header(self, width, height, msg):
        w, h = self._get_text_bound(msg=msg)

        _width = max(w + self.padding * 2, width, self.min_width)
        _height = max(h + self.padding * 2, min(height, self.min_height))
        header = Image.new('RGB', (_width, _height), color=self.bg_color)
        d = ImageDraw.Draw(header)
        d.text(((_width - w) / 2, (_height - h) / 2), msg, fill=self.text_color, font=self.font)
        return header

    def _get_text_bound(self, msg):
        draw = ImageDraw.Draw(Image.new('RGB', (0, 0), color='black'))
        w, h = draw.textsize(msg, font=self.font)
        return w, h

    def _merge(self, img0, img1):
        width0, height0 = img0.size
        width1, height1 = img1.size

        img = Image.new('RGB', (max(width0, width1), height0 + height1), color=self.bg_color)

        img.paste(img0, (0, 0))
        img.paste(img1, (0, height0))

        return img

    def _file_stat(self, path):
        stat = os.stat(path)
        try:
            return stat.st_birthtime
        except AttributeError:
            return stat.st_mtime

    def generate(self, source):

        files = []
        for file in os.listdir(source):
            full_path = os.path.join(source, file)

            if full_path.endswith('.jpg') or \
                    full_path.endswith('.png') or \
                    full_path.endswith('.jpeg'):
                stat = self._file_stat(full_path)
                files.append((stat, full_path))

        files.sort(key=lambda date: date[0])

        for i in range(len(files)):
            file = files[i][1]
            img_main = Image.open(file)

            width, height = img_main.size

            img_header = self._get_header(width, height, msg=self.page_format % (i + self.start_page))

            img = self._merge(img_header, img_main)

            yield i + self.start_page, img

    @classmethod
    def save(cls, generator, destination='generated', out_format='%d', show=False):
        os.makedirs(destination, exist_ok=True)
        for i, img in generator:
            if show:
                img.show()
            img.save(os.path.join(destination, out_format % i + '.jpg'))


if len(sys.argv) == 4:
    pg = Pager(bg_color='white',
               text_color='black',
               text_size=50,
               font_file=sys.argv[1],
               padding=10,
               page_format='Page %d')

    Pager.save(generator=pg.generate(source=sys.argv[2]),
               destination=sys.argv[3],
               out_format='%d',
               show=False)
else:
    raise RuntimeError('You must pass exactly two args, source and destination')
