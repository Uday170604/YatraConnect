from django.test import TestCase
from django.template import Template, Context

class TemplateSyntaxTest(TestCase):
    def test_syntax(self):
        t = Template("{% if value == 'M' %}Match{% endif %}")
        c = Context({"value": "M"})
        rendered = t.render(c)
        self.assertEqual(rendered, "Match")

    def test_syntax_no_spaces(self):
        # This SHOULD fail if Django is working as expected (it requires spaces)
        try:
            t = Template("{% if value=='M' %}Match{% endif %}")
            print("Rendered successfully (unexpected):", t.render(Context({"value": "M"})))
        except Exception as e:
            print("Caught expected error:", e)
