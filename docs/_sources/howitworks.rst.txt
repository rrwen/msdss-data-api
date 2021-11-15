How it Works
============

This package uses `FastAPI Users <https://fastapi-users.github.io/fastapi-users/>`_ to create an extended :class:`msdss_base_api:msdss_base_api.core.API` application.

Database operations are handled by :class:`msdss_base_database:msdss_base_database.core.Database` through the :class:`msdss_data_api.managers.DataManager` class, while data operation checks are handled by :class:`msdss_data_api.handlers.DataHandler`.

For user authentication and management, the :class:`msdss_users_api:msdss_users_api.core.UsersAPI` object is used to create user management routes and dependencies.

.. digraph:: methods

   rankdir=TB;

   baseapi[label="msdss-base-api" URL="https://rrwen.github.io/msdss-base-api/" style=filled];
   basedb[label="msdss-base-database" URL="https://rrwen.github.io/msdss-base-database/" style=filled];
   usersapi[label="msdss-users-api" URL="https://rrwen.github.io/msdss-users-api/" style=filled];

   datamanager[label="DataManager" shape=rect];
   datahandler[label="DataHandler" shape=rect];

   datamanagerfunc[label="create_data_manager_func" shape=rect style=rounded URL=""];
   getdatarouter[label="get_data_router" shape=rect style=rounded URL=""];

   subgraph cluster0 {
      label=< <B>msdss_data_api.core.DataAPI</B> >;
      style=rounded;

      basedb -> {datahandler;datamanager};
      datahandler -> datamanager -> getdatarouter;
      datamanagerfunc -> getdatarouter;
      {usersapi;getdatarouter} -> baseapi; 
   }
