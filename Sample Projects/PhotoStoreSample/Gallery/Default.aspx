<%@ Page Language="C#" AutoEventWireup="true" CodeBehind="Default.aspx.cs" Inherits="Gallery._Default" %>

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" >
<head runat="server">
    <title></title>
</head>
<body>
    <form id="form1" runat="server">
    <div>
    
        <asp:GridView ID="GridView1" runat="server" AutoGenerateColumns="False" 
            DataSourceID="SqlDataSource1">
            <Columns>
                <asp:BoundField DataField="Name" HeaderText="Name" SortExpression="Name" />
                <asp:BoundField DataField="Title" HeaderText="Title" SortExpression="Title" />
                <asp:BoundField DataField="Subject" HeaderText="Subject" 
                    SortExpression="Subject" />
                <asp:BoundField DataField="Rating" HeaderText="Rating" 
                    SortExpression="Rating" />
                <asp:BoundField DataField="Date Taken" HeaderText="Date Taken" 
                    SortExpression="Date Taken" />
                <asp:BoundField DataField="Copyright" HeaderText="Copyright" 
                    SortExpression="Copyright" />
                <asp:BoundField DataField="Camera Manufacturer" 
                    HeaderText="Camera Manufacturer" SortExpression="Camera Manufacturer" />
                <asp:BoundField DataField="Camera Model" HeaderText="Camera Model" 
                    SortExpression="Camera Model" />
                <asp:BoundField DataField="Thumbnail Path" HeaderText="Thumbnail Path" 
                    SortExpression="Thumbnail Path" />
                <asp:BoundField DataField="Full Path" HeaderText="Full Path" 
                    SortExpression="Full Path" />
            </Columns>
        </asp:GridView>
        <asp:SqlDataSource ID="SqlDataSource1" runat="server" 
            ConnectionString="<%$ ConnectionStrings:RepositoryConnectionString %>" 
            SelectCommand="Select * FROM [Gallery].[Gallery]"></asp:SqlDataSource>
    
    </div>
    </form>
</body>
</html>
