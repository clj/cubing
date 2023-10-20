import cmd
import re
import readline
import random

import click
from rubik.cube import Cube as _Cube
from rubik.cube import RIGHT
from rubik.cube import LEFT
from rubik.cube import UP
from rubik.cube import DOWN
from rubik.cube import FRONT
from rubik.cube import BACK
from rubik.cube import ROT_XZ_CW
from rubik.cube import ROT_XZ_CC
from rubik.cube import ROT_XY_CW
from rubik.cube import ROT_XY_CC

CmdError = object()

# fmt: off
_to_anim_mapping = [
    6, 7, 8, 3, 4, 5, 0, 1, 2,
    45, 48, 51, 46, 49, 52, 47, 50, 53,
    12, 24, 36, 13, 25, 37, 14, 26, 38,
    18, 30, 42, 19, 31, 43, 20, 32, 44,
    11, 10, 9, 23, 22, 21, 35, 34, 33,
    15, 27, 39, 16, 28, 40, 17, 29, 41,
]
_from_anim_mapping = [
    6, 7, 8, 3, 4, 5, 0, 1, 2,
    38, 37, 36, 18, 21, 24, 45, 48, 51,
    27, 30, 33, 41, 40, 39, 19, 22, 25,
    46, 49, 52, 28, 31, 34, 44, 43, 42,
    20, 23, 26, 47, 50, 53, 29, 32, 35,
    9, 12, 15, 10, 13, 16, 11, 14, 17,
]
_colour_index = [
    1, 1, 1, 1, 1, 1, 1, 1, 1,  # up
    0, 0, 0, 2, 2, 2, 0, 0, 0, 2, 2, 2,  # left/3, front/3, right/3, back/3
    0, 0, 0, 2, 2, 2, 0, 0, 0, 2, 2, 2,  # left/3, front/3, right/3, back/3
    0, 0, 0, 2, 2, 2, 0, 0, 0, 2, 2, 2,  # left/3, front/3, right/3, back/3
    1, 1, 1, 1, 1, 1, 1, 1, 1,  # down
    ]
_solved = "RRRRRRRRROOOOOOOOOYYYYYYYYYWWWWWWWWWGGGGGGGGGBBBBBBBBB"
# fmt: on


class Cube(_Cube):
    def Z(self):  self._rotate_pieces(self.pieces, ROT_XZ_CW)
    def Zi(self): self._rotate_pieces(self.pieces, ROT_XZ_CC)
    def Y(self):  self._rotate_pieces(self.pieces, ROT_XY_CW)
    def Yi(self): self._rotate_pieces(self.pieces, ROT_XY_CC)


def _mapping(faces, mapping):
    result = [None] * 54
    for dst, src in enumerate(mapping):
        result[dst] = faces[src]
    return "".join(result)


def to_anim(faces):
    return _mapping(faces, _to_anim_mapping)


def from_anim(faces):
    return _mapping(faces, _from_anim_mapping)


def pretty(faces):
    template = (
        "    {}{}{}\n"
        "    {}{}{}\n"
        "    {}{}{}\n"
        "{}{}{} {}{}{} {}{}{} {}{}{}\n"
        "{}{}{} {}{}{} {}{}{} {}{}{}\n"
        "{}{}{} {}{}{} {}{}{} {}{}{}\n"
        "    {}{}{}\n"
        "    {}{}{}\n"
        "    {}{}{}"
    )

    return "    " + template.format(*faces).strip()


def get_pieces(cube):
    right = [p for p in sorted(cube._face(RIGHT), key=lambda p: (-p.pos.y, -p.pos.z))]
    left = [p for p in sorted(cube._face(LEFT), key=lambda p: (-p.pos.y, p.pos.z))]
    up = [p for p in sorted(cube._face(UP), key=lambda p: (p.pos.z, p.pos.x))]
    down = [p for p in sorted(cube._face(DOWN), key=lambda p: (-p.pos.z, p.pos.x))]
    front = [p for p in sorted(cube._face(FRONT), key=lambda p: (-p.pos.y, p.pos.x))]
    back = [p for p in sorted(cube._face(BACK), key=lambda p: (-p.pos.y, -p.pos.x))]

    return (
        up
        + left[0:3]
        + front[0:3]
        + right[0:3]
        + back[0:3]
        + left[3:6]
        + front[3:6]
        + right[3:6]
        + back[3:6]
        + left[6:9]
        + front[6:9]
        + right[6:9]
        + back[6:9]
        + down
    )


class CubeShell(cmd.Cmd):
    intro = "Welcome to the cube shell.   Type help or ? to list commands.\n"
    prompt = "▦ > "
    cube = None
    moves = "LRUDFBMESXYZ"
    all_moves = (
        tuple(moves) + tuple(f"{m}'" for m in moves) + tuple(f"{m}2" for m in moves)
    )
    colours = "BGORWY"
    find_moves_re = re.compile(f"([{moves}]['2]?)")
    moves_re = re.compile(rf"^(?:[{moves}]['2]?\s*|\.\s*|{{.*?}}\s*)+$")
    colours_re = re.compile(rf"^((?:(?:F|FU|FRU):)?[{colours}]|[{colours}]{{2}})$")

    def parse_moves(self, moves):
        return self.find_moves_re.findall(moves.replace(" ", ""))

    def parse_print_faces(self, faces):
        parsed_faces = faces.split()
        parsed_faces = (
            m.group() if (m := self.colours_re.match(f)) else None for f in parsed_faces
        )
        parsed_faces = [
            ("".join(sorted(s)) if ":" not in s else s) for s in parsed_faces
        ]
        if "" in parsed_faces:
            return None

        return parsed_faces

    def precmd(self, line):
        if (
            line
            and (cmd := line.split(maxsplit=1)[0])
            not in ["help", "init", "quit", "EOF"]
            and hasattr(self, f"do_{cmd}")
            and self.cube is None
        ):
            print("Please run init to set up a cube")
            return ""
        return line

    def postcmd(self, stop, _):
        if stop is True:
            return stop
        elif stop is CmdError and self.cmdqueue:
            return True
        return False

    def emptyline(self):
        pass

    def default(self, line):
        if not self.moves_re.match(line):
            return super().default(line)
        self.do_move(line)

    def do_init(self, arg):
        if arg.startswith("scramble"):
            self.cube = Cube(from_anim(_solved))
            args = arg.split()
            if len(args) > 3:
                print("ERROR: Too many arguments")
            elif len(args) == 3:
                moves, seed = map(int, args[1:])
            elif len(args) == 2:
                moves, seed = int(args[1]), None
            else:
                moves, seed = 20, None
            random.seed(seed)
            moves = " ".join(random.choices(self.all_moves, k=moves))
            print(f"scramble: {moves}")
            self.do_move(moves)
        elif arg == "solved":
            self.cube = Cube(from_anim(_solved))
        else:
            arg = arg.replace(" ", "")
            if len(arg) != 54:
                print(
                    "ERROR: Argument must be a 'solved', 'scramble' or a 54 character string"
                )
                return CmdError

            self.cube = Cube(from_anim(arg))

    def do_pretty(self, arg):
        print(pretty(from_anim(self.do_print(arg, display=False))))

    do_pp = do_pretty

    def do_print(self, arg, display=True):
        if not arg:
            colours = to_anim(self.cube.flat_str())
        else:
            pieces = get_pieces(self.cube)

            faces = self.parse_print_faces(arg)

            def recolour(piece, idx):
                if "".join(sorted(filter(None, piece.colors))) in faces:
                    return piece.colors[idx]
                for face in (f for f in faces if ":" in f):
                    face_type, colours = face.split(":")
                    if (
                        len(tuple(filter(None, piece.colors))) == len(face_type)
                        and set(colours) <= set(piece.colors)
                        and piece.colors[idx] in colours
                    ):
                        return piece.colors[idx]
                return "L"

            colours = to_anim(
                "".join(recolour(p, idx) for p, idx in zip(pieces, _colour_index))
            )

        if display:
            print(colours)
        else:
            return colours

    do_p = do_print

    def do_echo(self, arg):
        print(arg)

    def do_move(self, arg):
        moves = self.parse_moves(arg)
        for move in moves:
            if move.replace(".", "") == "":
                continue
            move = move.replace("'", "i")
            count = 1
            if len(move) > 1 and re.match("^[0-9]+$", move[1:]):
                count = int(move[1:])
                move = move[0]
            move = getattr(self.cube, move)
            for i in range(count):
                move()

    def do_print_move(self, arg):
        print(re.sub("\s+", " ", arg))
        self.do_move(arg)

    def do_quit(self, _):
        return True

    def do_EOF(self, _):
        return True

    def do_break(self, _):
        self.cmdqueue = []
        try:
            readline.read_history_file("cube_history")
        except FileNotFoundError:
            pass


@click.group()
def cli():
    pass


@click.command()
def shell():
    try:
        readline.read_history_file("cube_history")
    except FileNotFoundError:
        pass
    try:
        CubeShell().cmdloop()
    finally:
        readline.write_history_file("cube_history")


@click.command()
@click.argument("script")
def run(script):
    shell = CubeShell()
    with open(script) as f:
        for line in (
            l
            for l in f.read().splitlines()
            if not (sl := l.strip()).startswith("#") or not sl
        ):
            if line.startswith(" "):
                shell.cmdqueue[-1] += "\n" + line
            else:
                shell.cmdqueue.append(line)
        # XXX: Make this optional
        shell.cmdqueue.append("quit")
    try:
        shell.cmdloop(intro="")
    finally:
        if readline.get_current_history_length():
            readline.write_history_file("cube_history")


cli.add_command(shell)
cli.add_command(run)


if __name__ == "__main__":
    cli()
