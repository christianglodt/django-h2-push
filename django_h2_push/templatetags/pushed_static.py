from django import template
from django.templatetags.static import StaticNode

register = template.Library()


class PushedStaticNode(StaticNode):
    def __init__(self, varname=None, path=None, preload_as=''):
        self.preload_as = preload_as
        super(PushedStaticNode, self).__init__(varname, path)

    def render(self, context):
        rendered = url = super(PushedStaticNode, self).render(context)
        if not url:
            url = self.url(context)
        if url:
            request = context.get('request')
            if request:
                if not hasattr(request, '_h2_push_store'):
                    request._h2_push_store = set()
                request._h2_push_store.add((url, self.preload_as))
        return rendered

    @classmethod
    def handle_token(cls, parser, token):
        """
        Class method to parse prefix node and return a Node.
        """
        bits = token.split_contents()

        if len(bits) < 2:
            raise template.TemplateSyntaxError(
                "'%s' takes at least one argument (path to file)" % bits[0])

        path = parser.compile_filter(bits[1])

        varname = None
        preload_as = 'prefetch'
        rest = bits[2:]
        while len(rest) > 0:
            kw = rest.pop(0)
            if kw == 'as':
                varname = rest.pop(0)
            if kw == 'preload_as':
                preload_as = rest.pop(0)

        return cls(varname, path, preload_as)


@register.tag('pushed_static')
def do_pushed_static(parser, token):
    return PushedStaticNode.handle_token(parser, token)
