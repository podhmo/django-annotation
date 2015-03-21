django-annotation
========================================

when model definition

.. code-block:: python

   import django_annoation as d

   class Person(models.Model):
       name = d.CharField(max_length=255, verbose_name="Name", doc="名前")


when view

.. code-blocok:: python

   import django_annotation as d
   user = User.objects.get()
   d.get_mapping(user) # => {"doc": "名前"}



