import click


def command(either=None):
    if either is None:
        either = []

    class CommandOptionsTogether(click.Command):
        def invoke(self, ctx):
            eit = [list(t) for t in either]

            for opts in eit:
                if sum([ctx.params[opt] is not None for opt in opts]) > 1:
                    opts = ", ".join([f"--{o}" for o in opts])
                    msg = f"The options [{opts}] are mutually exclusive."
                    raise click.ClickException(msg)

            super(CommandOptionsTogether, self).invoke(ctx)

    return CommandOptionsTogether
