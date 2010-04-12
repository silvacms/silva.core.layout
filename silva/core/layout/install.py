# Copyright (c) 2002-2010 Infrae and contributors. All rights
# reserved. See also LICENSE.txt
# $Id$

# Python
from os import path
# Zope
from App.Common import package_home

metadatasets = [('silva-layout', 'silvalayout.xml',
                 ('Silva Root', 'Silva Publication')),
                ]

installed_attr = "__silva_layout_installed__"

def is_installed(context):
    return hasattr(context, installed_attr)

def install(context, default_skinid='SilvaLegacy'):
    # configure metadata
    configureMetadata(context)
    # set initial skin on Silva Root object, if doesn't have a setting yet
    setInitialSkin(context.get_root(), default_skinid)
    setattr(context, installed_attr, 1)

def uninstall(context):
    resetMetadata(context, ['silva-layout', ])
    delattr(context, installed_attr)

def configureMetadata(context):
    product = package_home(globals())
    schema = path.join(product, 'schema')

    for setid, xmlfilename, types in metadatasets:
        collection = context.service_metadata.getCollection()
        if not setid in collection.objectIds():
            xmlfile = path.join(schema, xmlfilename)
            definition = open(xmlfile, 'r')
            collection.importSet(definition)

        context.service_metadata.addTypesMapping(types, (setid, ))
    context.service_metadata.initializeMetadata()

def setInitialSkin(silvaroot, default_skinid):
    setid = 'silva-layout'
    metadataservice = silvaroot.service_metadata
    currentskin = metadataservice.getMetadataValue(silvaroot, setid, 'skin')
    if not currentskin:
        binding = metadataservice.getMetadata(silvaroot)
        binding.setValues(setid, {'skin': default_skinid})

def resetMetadata(root, metadatasets):
    """Removes metadata sets from the metadata mapping."""
    mapping = root.service_metadata.getTypeMapping()
    default = ''
    # Get all content types that have a metadata mapping
    content_types =  [item.id for item in mapping.getTypeMappings()]
    tm = []
    # Remove the metadata sets for each content type
    for content_type in content_types:
        chain = mapping.getChainFor(content_type)
        sets = [set.strip() for set in chain.split(',')]
        sets_to_remove = []
        for set in sets:
            if set in metadatasets:
                sets_to_remove.append(set)
        for set in sets_to_remove:
            sets.remove(set)
        map = {'type':content_type,
               'chain':', '.join(sets)}
        tm.append(map)
    mapping.editMappings(default, tm)

    # Remove the metadata set specifications
    root.service_metadata.collection.manage_delObjects(metadatasets)
