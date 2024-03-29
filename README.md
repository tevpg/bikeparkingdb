# bikeparkingdb
Database and web reporting for bike parking data

This work incorporates code (c) Julias Hocking and Todd Glover 2023-2024 in https://github.com/ironwoodcall/tagtracker

Back end database and web for tracking and reporting on bike parking services such as bike valet

Functional groups:
- schema for common data exchange format
- scripts to convert from various formats (tagtracker, two-wheel valet, templated google sheets) to common data exchange format
- loaders to load database from exchange format files into database
- cgi scripts to provide reports and access to the data

Supports data from multiple organizations operating parking services at multiple sites, such that users within an organization can see only their own data
