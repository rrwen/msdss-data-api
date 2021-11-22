How it Works
============

This package uses `FastAPI Users <https://fastapi-users.github.io/fastapi-users/>`_ to create an extended :class:`msdss_base_api:msdss_base_api.core.API` application.

Database operations are handled by :class:`msdss_base_database:msdss_base_database.core.Database` through the :class:`msdss_data_api.managers.DataManager` class, while data operation checks are handled by :class:`msdss_data_api.handlers.DataHandler`. Similarly, metadata is handled via the :class:`msdss_data_api.managers.MetadataManager` class, but using a single table.

Request bodies with known parameters are represented with models in the :mod:`msdss_data_api.models` module.

For user authentication and management, the :class:`msdss_users_api:msdss_users_api.core.UsersAPI` object is used to create user management routes and dependencies.

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
   metadatamanager[label="MetaDataManager" shape=rect];

   datamanagerfunc[label="create_data_manager_func" shape=rect style=rounded URL=""];
   getdatarouter[label="get_data_router" shape=rect style=rounded URL=""];

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

      datamanagerfunc -> getdatarouter;
      {usersapi;getdatarouter} -> baseapi; 
   }
