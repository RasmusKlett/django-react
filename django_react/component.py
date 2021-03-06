import sys
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import six
from django.utils.safestring import mark_safe
from .exceptions import PropSerializationError, RenderingError
from .render import render_component


class ReactComponent(object):
    path_to_source = None
    props = None
    serialized_props = None
    json_encoder_class = DjangoJSONEncoder

    def __init__(self, path_to_source, **kwargs):
        self.path_to_source = path_to_source
        self.props = kwargs

    def render_to_string(self):
        """
        Render a component to its initial HTML. You can use this method to generate HTML
        on the server and send the markup down on the initial request for faster page loads
        and to allow search engines to crawl you pages for SEO purposes.
        """

        # While rendering templates Django will silently ignore some types of exceptions,
        # so we need to intercept them and raise our own class of exception
        try:
            return mark_safe(
                render_component(
                    path_to_source=self.path_to_source,
                    serialized_props=self.get_serialized_props(),
                )
            )
        except (TypeError, AttributeError) as e:
            six.reraise(RenderingError, RenderingError(*e.args), sys.exc_info()[2])

    def render_to_static_markup(self):
        """
        Similar to `ReactComponent.render_to_string`, except this doesn't create
        extra DOM attributes such as `data-react-id`, that React uses internally.
        This is useful if you want to use React as a simple static page generator,
        as stripping away the extra attributes can save lots of bytes.
        """

        # While rendering templates Django will silently ignore some types of exceptions,
        # so we need to intercept them and raise our own class of exception
        try:
            return mark_safe(
                render_component(
                    path_to_source=self.path_to_source,
                    serialized_props=self.get_serialized_props(),
                    to_static_markup=True,
                )
            )
        except (TypeError, AttributeError) as e:
            six.reraise(RenderingError, RenderingError(*e.args), sys.exc_info()[2])

    def get_serialized_props(self):
        """
        Returns the ReactComponent's props as a JSON string
        """

        if self.serialized_props:
            return self.serialized_props

        # While rendering templates Django will silently ignore some types of exceptions,
        # so we need to intercept them and raise our own class of exception
        try:
            self.serialized_props = mark_safe(
                json.dumps(self.props, cls=self.json_encoder_class)
            )
        except (TypeError, AttributeError) as e:
            six.reraise(PropSerializationError, PropSerializationError(*e.args), sys.exc_info()[2])

        return self.serialized_props