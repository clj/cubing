import cmd
import mimetypes
import os
import re
import readline
import random
import textwrap

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
import jinja2
import jinja2.nodes
import jinja2.ext
import mistune
import livereload
import wsgiref.util

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
    def Z(self):
        self._rotate_pieces(self.pieces, ROT_XZ_CW)

    def Zi(self):
        self._rotate_pieces(self.pieces, ROT_XZ_CC)

    def Y(self):
        self._rotate_pieces(self.pieces, ROT_XY_CW)

    def Yi(self):
        self._rotate_pieces(self.pieces, ROT_XY_CC)


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
    colours_re = re.compile(
        rf"^((?:(?:F|FU|FRU):)?[{colours}\*\~]{{1,3}}|[{colours}]{{2}})$"
    )
    print_fn = print

    def parse_moves(self, moves):
        moves = re.sub("{.*}", "", moves)
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
        self.print_fn(pretty(from_anim(self.do_print(arg, display=False))))

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
                    face_type, colours_def = face.split(":")
                    colours = re.findall(f"(?<!~)[{self.colours}\*]", colours_def)
                    not_colours = re.findall(f"(?<=~)[{self.colours}]", colours_def)
                    if (
                        len(tuple(filter(None, piece.colors))) == len(face_type)
                        and (set(colours) - set("*")) <= set(piece.colors)
                        and (piece.colors[idx] in colours or "*" in colours)
                        and (set(piece.colors).isdisjoint(set(not_colours)))
                    ):
                        return piece.colors[idx]
                return "L"

            colours = to_anim(
                "".join(recolour(p, idx) for p, idx in zip(pieces, _colour_index))
            )

        if display:
            self.print_fn(colours)
        else:
            return colours

    do_p = do_print

    def do_echo(self, arg):
        self.print_fn(arg)

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
        self.print_fn(re.sub("\s+", " ", arg))
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


def _parse_script_file(lines):
    commands = []
    for line in (
        sl
        for l in lines
        if (not (sl := l.rstrip()).startswith("#"))
        and not l.lstrip().startswith("#")
        and sl
    ):
        if line.startswith(" "):
            commands[-1] += "\n" + line
        else:
            commands.append(line)
    return commands


@click.command()
@click.argument("script")
def run(script):
    shell = CubeShell()
    with open(script) as f:
        shell.cmdqueue = _parse_script_file(f)
        shell.cmdqueue.append("quit")  # XXX: Make this optional
    try:
        shell.cmdloop(intro="")
    finally:
        if readline.get_current_history_length():
            readline.write_history_file("cube_history")


class CubeExt(jinja2.ext.Extension):
    tags = {"cube"}

    def parse(self, parser):
        lineno = next(parser.stream).lineno

        args = {"target_cube": "default"}
        target_variable = None
        cmd = "exec_only"
        if parser.stream.current.type != "block_end":
            if parser.stream.next_if("lbracket"):
                args["target_cube"] = parser.stream.expect("name").value
                parser.stream.expect("rbracket")
            if cmd_node := parser.stream.next_if("name"):
                cmd = cmd_node.value
                if cmd == "set":
                    target_variable = parser.stream.expect("name").value
                elif cmd == "copy":
                    args["src"] = parser.stream.expect("name").value
                    args["dst"] = (
                        d.value if (d := parser.stream.next_if("name")) else None
                    )
                    if args["src"] and not args["dst"]:
                        args["dst"] = args["src"]
                        args["src"] = "default"

        if cmd == "copy":
            body = jinja2.nodes.Const(None)
        else:
            body = parser.parse_statements(["name:endcube"], drop_needle=True)

            if len(body[0].nodes) > 1:
                token = body[0].nodes[1]
                raise jinja2.TemplateSyntaxError(
                    "Jinja not allowed in `cube` blocks",
                    token.lineno,
                    parser.stream.name,
                    parser.stream.filename,
                )

            body = jinja2.nodes.Const(body[0].nodes[0].data)

        nodes = [
            jinja2.nodes.If(
                jinja2.nodes.Not(jinja2.nodes.Name("_cube_shells", "load")),
                [
                    jinja2.nodes.Assign(
                        jinja2.nodes.Name("_cube_shells", "store"),
                        jinja2.nodes.Dict([]),
                    )
                ],
                [],
                [],
            ).set_lineno(lineno),
        ]

        call = self.call_method(
            "_cube_cmd",
            [
                jinja2.nodes.Const(cmd),
                jinja2.nodes.Name("_cube_shells", "load"),
                jinja2.nodes.Dict(
                    [
                        jinja2.nodes.Pair(
                            jinja2.nodes.Const(k),
                            jinja2.nodes.Const(v),
                        )
                        for k, v in args.items()
                    ]
                ),
                body,
            ],
        ).set_lineno(lineno)

        if target_variable:
            nodes.append(
                jinja2.nodes.Assign(
                    jinja2.nodes.Name(target_variable, "store"),
                    jinja2.nodes.MarkSafe(call),
                ).set_lineno(lineno)
            )
        else:
            nodes.append(jinja2.nodes.ExprStmt(call))

        return nodes

    def _cube_cmd(self, cmd, cube_shells, args, script):
        def new_cube_shell():
            shell = CubeShell()
            shell.print_fn = None
            return shell

        if cmd == 'copy':
            shell = new_cube_shell()
            shell.cube = Cube(cube_shells[args['src']].cube)
            cube_shells[args['dst']] = shell
            return

        output = ""

        def print_fn(line):
            nonlocal output
            output += line

        if (shell := cube_shells.get(args["target_cube"])) is None:
            cube_shells[args["target_cube"]] = shell = new_cube_shell()

        shell.print_fn = print_fn
        for line in _parse_script_file(script.splitlines()):
            line = shell.precmd(line)
            stop = shell.onecmd(line)
            stop = shell.postcmd(stop, line)
            # XXX: do something with stop

        shell.print_fn = None

        return output


class MistuneExt(jinja2.ext.Extension):
    tags = {"md"}

    def parse(self, parser):
        lineno = next(parser.stream).lineno

        body = parser.parse_statements(["name:endmd"], drop_needle=True)

        return jinja2.nodes.CallBlock(
            self.call_method("markdown"), [], [], body
        ).set_lineno(lineno)

    def markdown(self, caller):
        return mistune.html(textwrap.dedent(caller()))


class LiveReloadFileSystemLoader(jinja2.FileSystemLoader):
    def __init__(self, reload_server, searchpath, encoding="utf-8", followlinks=False):
        super().__init__(searchpath, encoding, followlinks)
        self.reload_server = reload_server
        self.added = set()

    def get_source(self, environment, template):
        (source, filename, uptodate) = super().get_source(environment, template)
        if filename not in self.added:
            self.reload_server.watch(filename)
        return (source, filename, uptodate)


def _jinja2_env(loader):
    env = jinja2.Environment(
        loader=loader,
        autoescape=jinja2.select_autoescape(),
        extensions=[CubeExt, MistuneExt],
    )
    return env


def _render(env, source):
    template = env.get_template(source)
    output = template.render()

    return output


@click.command()
@click.argument("source")
def render(source):
    env = _jinja2_env(jinja2.FileSystemLoader("."))
    output = _render(env, source)

    print(output)


@click.command()
@click.argument("source")
def serve(source):

    def app(environ, start_response):
        path = environ["PATH_INFO"]
        if path == "/":
            status = "200 OK"
            headers = [("Content-type", "text/html; charset=utf-8")]

            start_response(status, headers)

            output = _render(env, source)

            return [output.encode("utf-8")]

        filename = environ["PATH_INFO"][1:]
        mime_type = mimetypes.guess_type(filename)[0]

        if os.path.exists(filename):
            start_response("200 OK", [("Content-Type", mime_type)])
            return wsgiref.util.FileWrapper(open(filename, "rb"))
        else:
            start_response("404 Not Found", [("Content-Type", "text/plain")])
            return [b"not found"]

    server = livereload.Server(app)
    env = _jinja2_env(LiveReloadFileSystemLoader(server, "."))
    server.watch(source)
    server.serve()


cli.add_command(shell)
cli.add_command(run)
cli.add_command(render)
cli.add_command(serve)


if __name__ == "__main__":
    cli()
