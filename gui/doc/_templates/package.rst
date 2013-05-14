{{ fullname }}
===========================================================

.. automodule:: {{ fullname }}




{% block classes %}
{% if classes %}

.. rubric:: Classes

.. autosummary::
   :nosignatures:
   :toctree: {{ objname  }}/
   :template: class.rst

{% for item in classes %}
   {{ item }}
{%- endfor %}
{% endif %}
{% endblock %}

{% block functions %}
{% if functions %}

.. rubric:: Functions
   
.. autosummary::
   :toctree: {{ objname  }}/
   :template: function.rst

{% for item in functions %}
   {{ item }}
{%- endfor %}
{% endif %}
{% endblock %}



{% block submodules %}
{% if submodules %}

Modules
-------

.. autosummary::
   :toctree: {{ objname  }}/
   :template: module.rst

{% for item in submodules %}
   {{ item }}
{%- endfor %}
{% endif %}
{% endblock %}

{% block exceptions %}
{% if exceptions %}

Exceptions
----------

.. autosummary::
   :toctree: {{ objname  }}/
   :template: exception.rst

{% for item in exceptions %}
   {{ item }}
{%- endfor %}
{% endif %}
{% endblock %}

.. template package.rst
