How it Works
============

This package creates an extended :class:`msdss_base_api:msdss_base_api.core.API` application using :class:`msdss_data_api.core.DataAPI`.
The ``DataAPI`` class uses :func:`msdss_data_api.routers.get_data_router` to setup routes for managing data.
Data management is handled by managers in :mod:`msdss_data_api.managers`, which uses handlers in :mod:`msdss_data_api.handlers` to check route inputs.
The general process is: ``handlers -> managers -> get_data_router -> DataAPI``.

**Other notes:**

* Database operations are handled by :class:`msdss_base_database:msdss_base_database.core.Database`
* Request bodies with known parameters are represented with models in the :mod:`msdss_data_api.models` module
* For user authentication and management, the :class:`msdss_users_api:msdss_users_api.core.UsersAPI` object is used to create user management routes and dependencies

.. digraph:: methods

   compound=true;
   rankdir=TB;
   graph [pad="0.75", nodesep="0.25", ranksep="1"];

   baseapi[label="msdss-base-api" URL="https://rrwen.github.io/msdss-base-api/" style=filled];
   basedb[label="msdss-base-database" URL="https://rrwen.github.io/msdss-base-database/" style=filled];
   usersapi[label="msdss-users-api" URL="https://rrwen.github.io/msdss-users-api/" style=filled];

   datacreatemodel[label="DataCreate" shape=rect];
   metadataupdatemodel[label="MetadataUpdate" shape=rect];

   datamanager[label="DataManager" shape=rect];
   datahandler[label="DataHandler" shape=rect];
   metadatamanager[label="MetadataManager" shape=rect];

   metadatafunc[label="create_metadata_manager_func" shape=rect style=rounded];
   datamanagerfunc[label="create_data_manager_func" shape=rect style=rounded];
   getdatarouter[label="get_data_router" shape=rect style=rounded];

   subgraph cluster0 {
      label=< <B>msdss_data_api.core.DataAPI</B> >;
      style=rounded;

      subgraph cluster1 {
         label=< <B>msdss_data_api.models</B> >;
         datacreatemodel;
         metadataupdatemodel;
      }
      metadataupdatemodel -> getdatarouter[lhead=cluster1 ltail=cluster1];

      subgraph cluster2 {
         label=< <B>msdss_data_api.managers</B> >;
         datamanager;
         metadatamanager;
      }
      datamanager -> getdatarouter[lhead=cluster2 ltail=cluster2];
      datahandler -> datamanager[lhead=cluster2 ltail=cluster2];
      basedb -> {datahandler;metadatamanager}[lhead=cluster2 ltail=cluster2];

      subgraph cluster3 {
         label=< <B>msdss_data_api.tools</B> >;
         datamanagerfunc;
         metadatafunc;
      }
      datamanagerfunc -> getdatarouter[lhead=cluster3 ltail=cluster3];

      {usersapi;getdatarouter} -> baseapi;
   }
