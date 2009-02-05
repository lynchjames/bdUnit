if (OBJECT_ID('[dbo].[DropSchemaObjects]', 'P') is not null)
   drop procedure [dbo].[DropSchemaObjects]
go
create procedure [dbo].[DropSchemaObjects]
   @schemaName sysname
as
begin
   set nocount on
   
   declare @dropStatement nvarchar(500)
   declare @order int
 
   -- The following deletes "Oslo" repository specific
   -- data related to the target schema.
   if(SCHEMA_ID('Repository') is not null)
   begin
      delete from [Repository].[IdSequencesTable] where [schema] = @schemaName;
      delete from [Repository].[IdSequenceAliasesTable] where [schema] = @schemaName;
   end
 
   -- Delete Repository.Catalog.Sql Registration for Schema Objects
   --
   -- Store a list of roles associated with the target schema and
   -- their relationship identifiers. Use to delete them later.
   if(SCHEMA_ID('Repository.Catalog.Sql') is not null)
   begin
      if (object_id('tempdb.dbo.#roles', 'U') is not null)
         drop table #roles;
      select distinct R.Id as RoleIdToDelete, R.Relationship as RelationshipToDelete
      into #roles
      from [Repository.Catalog.Sql].[Roles] R
      inner join [Repository.Catalog.Sql].[Columns] C on (C.Id = R.RolePlayerColumn or
         C.Id = R.RoleColumn)
      inner join sys.objects O on (O.[object_id] = C.[Object])
      where O.[schema_id] = SCHEMA_ID(@schemaName)
 
      delete [Repository.Catalog.Sql].[Roles]
      where Id in (select RoleIdToDelete from #roles)
 
      delete [Repository.Catalog.Sql].[Relationships]
      where Id in (select distinct RelationshipToDelete from #roles)
 
      delete C
      from [Repository.Catalog.Sql].[Columns] C
      where C.[Object] in (select [object_id] from sys.objects O 
                     where O.[schema_id] = SCHEMA_ID(@schemaName))
 
      delete V
      from [Repository.Catalog.Sql].[ViewsTable] V
      where V.Id in (select O.[object_id] from sys.objects O
                     where O.[schema_id] = SCHEMA_ID(@schemaName))
 
      delete S
      from [Repository.Catalog.Sql].[Schemas] S
      where S.Id = SCHEMA_ID(@schemaName)
 
      delete SI
      from [Repository.Catalog.Sql].[SchemaItems] SI
      where (SI.Kind in (2,3) and 
            MajorId in (select O.[object_id] from sys.objects O
                        where O.[schema_id] = SCHEMA_ID(@schemaName)))
            or
            (SI.Kind=1 and
            MajorId=SCHEMA_ID(@schemaName))
            or
            (SI.Kind=5 and
            MajorId in (select RoleIdToDelete from #roles))
            or
            (SI.Kind=4 and
            MajorId in (select RelationshipToDelete from #roles))
   end
   
   -- Delete SQL schema along with all associated objects.
   declare schemaObjectsCursor cursor for 
   select 
      case o.[type]
         when 'TF'   then 'drop function ' + QUOTENAME(@schemaName) + '.' + QUOTENAME(o.[name])
         when 'IF'   then 'drop function ' + QUOTENAME(@schemaName) + '.' + QUOTENAME(o.[name])
         when 'FN'   then 'drop function ' + QUOTENAME(@schemaName) + '.' + QUOTENAME(o.[name])
         when 'P'    then 'drop procedure ' + QUOTENAME(@schemaName) + '.' + QUOTENAME(o.[name])
         when 'PK'   then 'alter table ' + QUOTENAME(@schemaName) + '.' + QUOTENAME(p.[name]) + 
                           ' drop constraint ' + QUOTENAME(o.[name])
         when 'F'    then 'alter table ' + QUOTENAME(@schemaName) + '.' + QUOTENAME(p.[name]) + 
                           ' drop constraint ' + QUOTENAME(o.[name])
         when 'TR'   then 'drop trigger ' + QUOTENAME(@schemaName) + '.' + QUOTENAME(o.[name])
         when 'V'    then 'drop view ' +     QUOTENAME(@schemaName) + '.' + QUOTENAME(o.[name])
         when 'IT'   then 'drop table ' + QUOTENAME(@schemaName) + '.' + QUOTENAME(o.[name])
         when 'U'    then 'drop table ' + QUOTENAME(@schemaName) + '.' + QUOTENAME(o.[name])
         else '-- Unecessary to drop ' + QUOTENAME(o.[name]) + '.' end,
      [order] = case o.[type]
         when 'P'     then 1
         when 'IF'    then 2
         when 'TF'    then 3
         when 'FN'    then 4
         when 'F'     then 5
         when 'PK'    then 6
         when 'TR'    then 7
         when 'V'     then 8
         when 'IT'    then 9
         when 'U'     then 10
         else 100 end
   from sys.objects o 
   left outer join sys.objects p on o.[parent_object_id] = p.[object_id]
   where o.[schema_id] = SCHEMA_ID(@schemaName)
   -- Also drop foreign keys from other schemas that reference the
   -- target schema but will not be dropped themselves.
   union all
   select 
      'alter table ' + QUOTENAME(SCHEMA_NAME(FK.[schema_id])) + '.' + 
         QUOTENAME(OBJECT_NAME(FK.[parent_object_id])) + 
         ' drop constraint ' + QUOTENAME(FK.[name]),
      [order] = 5
   from sys.foreign_keys FK
   inner join sys.objects O on O.[object_id] = FK.referenced_object_id
   where O.[schema_id] = SCHEMA_ID(@schemaName)
            and FK.[schema_id] != SCHEMA_ID(@schemaName)
   -- Also drop user degined types for the schema.
   union all
   select
      'drop type ' + QUOTENAME(SCHEMA_NAME(T.[schema_id])) + '.' +
         QUOTENAME(T.[name]),
      [order] = 11
   from sys.types T
   where T.[schema_id] = SCHEMA_ID(@schemaName)
   -- Also drop xml schema collections for the schema.
   union all
      select
      'drop xml schema collection ' + QUOTENAME(SCHEMA_NAME(X.[schema_id])) + '.' +
         QUOTENAME(X.[name]),
      [order] = 12
      from sys.xml_schema_collections X
      where X.[schema_id] = SCHEMA_ID(@schemaName)   
   order by [order];    
 
   -- This loop attempts to drop dependent objects in several passes.
   -- It will not work with circular dependencies. 
   while exists (select name from sys.objects O where O.[schema_id] = SCHEMA_ID(@schemaName)
                 union all select name from sys.types T where T.[schema_id] = SCHEMA_ID(@schemaName)
                 union all select name from sys.xml_schema_collections X where X.[schema_id] = SCHEMA_ID(@schemaName))
   begin
      open schemaObjectsCursor
      fetch next from schemaObjectsCursor into @dropStatement, @order
      while @@fetch_status = 0
      begin
         begin try 
            print (@dropStatement);
            execute (@dropStatement);                  
         end try
         begin catch end catch;
         fetch next from schemaObjectsCursor into @dropStatement, @order
      end;
      close schemaObjectsCursor
   end;
 
   deallocate schemaObjectsCursor;
 
   if (SCHEMA_ID(@schemaName) is not null)
   begin
      set @dropStatement = 'drop schema ' + QUOTENAME(@schemaName);
      print '';
      print (@dropStatement);
      execute (@dropStatement);                  
   end;
end;
go
 
dbo.DropSchemaObjects 'Gallery'
go