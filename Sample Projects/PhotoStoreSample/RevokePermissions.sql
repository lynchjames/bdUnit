-- Revoke read on folder 100 from DOMAIN\USER
exec [Item].[RevokePrincipalPermission]    
    @principal = N'DOMAIN\USER',
    @resource = 100,
    @operation = 'BA21FDED-D87D-462E-C480-34EEED30CA5D', 
    @resourceKind = 'FD900DC4-9E3B-451F-0087-5B536D166AB0';
