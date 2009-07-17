#region Using Statements

using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using bdUnit.Interfaces;
using NUnit.Framework;
using StructureMap;
using System;

#endregion

namespace bdUnit.Interfaces
{


    public partial interface IUser
    {
        IUser Spouse { get; set; }
        string Name { get; set; }
        string LastName { get; set; }
        bool UnMarried { get; set; }
        bool IsDead { get; set; }
        int Age { get; set; }
        DateTime CreatedDate { get; set; }
        ILocation Location { get; set; }
        IList<IUser> Children { get; set; }
        void Kill(IUser user);
        void ProposeTo(IUser user);
        void Marry(IUser user);
        void Meet(IList<IUser> user);
        void Locate();
        void Find();
    }

    public partial interface ISleepShop
    {
        ILocation Location { get; set; }
        bool IsOpen { get; set; }
        void Find();
    }

    public partial interface ILocation
    {
        double Latitude { get; set; }
        double Longitude { get; set; }
    }
}

namespace bdUnit.Tests
{
    [TestFixture]
    [Ignore]
    public class LogansRun
    {
        [TestFixtureSetUp]
        public void Setup()
        {
            StructureMapInitializer.Initialize();
        }


        [Test]
        public void When_User_ProposeTo_User()
        {
            IUser Peter = ObjectFactory.GetInstance<IUser>();
            IUser Patty = ObjectFactory.GetInstance<IUser>();
            Peter.ProposeTo(Patty);
            Peter.Marry(Patty);
            Peter.Name = "Peter";
            Patty.Name = "Patty";
            Assert.IsTrue(Peter.LastName == Patty.LastName, "Failed: Peter.LastName == Patty.LastName");
            Assert.IsTrue(!Peter.UnMarried, "Failed: !Peter.UnMarried");
            Assert.IsTrue(Peter.Age < 21, "Failed: Peter.Age < 21");
            Assert.IsTrue(!Patty.UnMarried, "Failed: !Patty.UnMarried");
            Assert.IsTrue(Patty.Age < 21, "Failed: Patty.Age < 21");
            Assert.IsTrue(Peter.Spouse == Patty, "Failed: Peter.Spouse == Patty");
            Assert.IsTrue(Patty.Spouse == Peter, "Failed: Patty.Spouse == Peter");
        }

        [Test]
        public void When_UnMarried_Is_Set()
        {
            IUser user = ObjectFactory.GetInstance<IUser>();

            user.UnMarried = true;
            IUser user1 = ObjectFactory.GetInstance<IUser>();

            user1.Name = "James";
            Assert.IsTrue(user.IsDead, "Failed: user.IsDead");
            var dateTime0 = DateTime.Parse("22/04/2010");
            Assert.IsTrue(user.CreatedDate < dateTime0, "Failed: user.CreatedDate < dateTime0");
            Assert.IsTrue(user.Children.Count < 3, "Failed: user.Children.Count < 3");
        }

        [Test]
        public void When_Name_Is_Set()
        {
            IUser user = ObjectFactory.GetInstance<IUser>();

            user.Name = "Logan";
            IUser user1 = ObjectFactory.GetInstance<IUser>();

            user1.Name = "Blah";
            var dateTime20 = DateTime.Parse("22/04/2010");
            var dateTime21 = DateTime.Parse("22/04/2020");
            if (user.IsDead && user.CreatedDate > dateTime21)
            {
                Assert.IsTrue(user.IsDead, "Failed: user.IsDead");
                Assert.IsTrue(!user.Name.Contains("Log"), "Failed: !user.Name.Contains(\"Log\")");
                Assert.IsTrue(!user.Children.Contains(user1), "Failed: !user.Children.Contains(user1)");
                Assert.IsTrue(!user.Children.Any(x => x.Name == user1.Name), "Failed: !user.Children.Any(x => x.Name == user1.Name)");
                Assert.IsTrue(user.Name != user1.Name, "Failed: user.Name != user1.Name");

            }
            else if (user.CreatedDate == dateTime20)
            {
                Assert.IsTrue(user.Children.Count < 3, "Failed: user.Children.Count < 3");

            }
            else
            {
                Assert.IsTrue(user.Children.Count > 3, "Failed: user.Children.Count > 3");

            }


        }

    }
}