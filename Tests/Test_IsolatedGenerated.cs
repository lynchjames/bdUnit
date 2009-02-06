#region Using Statements

using System;
using System.Collections.Generic;
using System.Diagnostics;
using bdUnit.Interfaces;
using NUnit.Framework;
using StructureMap;

#endregion

namespace bdUnit.Interfaces
{

    [PluginFamily("bdUnit")]
    public interface IUser
    {
        IUser Spouse { get; set; }
        bool IsARunner { get; set; }
        int Age { get; set; }
        bool IsDead { get; set; }
        IList<IPerson> Children { get; set; }
        void Kill(IUser user);
        void Marry(IUser user);
        void Visit(ISleepShop sleepshop);
        void Total();
    }

    [PluginFamily("bdUnit")]
    public interface ISleepShop
    {
        ILocation Location { get; set; }
        bool IsOpen { get; set; }
        void Locate();
    }

    [PluginFamily("bdUnit")]
    public interface ILocation
    {
        decimal Latitude { get; set; }
        decimal Longitude { get; set; }
    }

    public interface IPerson
    {

    }
}

namespace Tests
{

}

namespace bdUnit.Tests
{
    [TestFixture]
    public class LogansRun_Marriage
    {
        [TestFixtureSetUp]
        
        public void Set()
        {
            ObjectFactory.Initialize(
            x => x.Scan(scanner =>
            {
                var location = AppDomain.CurrentDomain.BaseDirectory;
                scanner.AssembliesFromPath(location);
                scanner.WithDefaultConventions();
            }));
        }

        [Test]
        public void When_User_Marry_User()
        {
            Debug.Write(ObjectFactory.WhatDoIHave());
            var Peter = ObjectFactory.GetNamedInstance<IUser>("bdUnit");
            var Eve = ObjectFactory.GetNamedInstance<IUser>("bdUnit");
            Peter.Marry(Eve);
            Assert.IsTrue(!Peter.IsARunner);
            Assert.IsTrue(Peter.Age < 30);
            Assert.IsTrue(Peter.Spouse == Eve);
            Assert.IsTrue(Eve.Spouse == Peter);
        }

        [Test]
        public void When_User_Kill_User()
        {
            //ObjectFactory.Initialize(
            //    x => x.Scan(scanner =>
            //    {
            //        var location = AppDomain.CurrentDomain.BaseDirectory;
            //        scanner.AssembliesFromPath(location);
            //        scanner.WithDefaultConventions();
            //    }));
            var a = ObjectFactory.GetNamedInstance<IUser>("bdUnit");
            var b = ObjectFactory.GetNamedInstance<IUser>("bdUnit");
            a.Kill(b);
            Assert.IsTrue(b.IsDead);
            Assert.IsTrue(!a.IsDead);
        }

        [Test]
        public void When_User_Visit_SleepShop()
        {
            //ObjectFactory.Initialize(
            //    x => x.Scan(scanner =>
            //    {
            //        var location = AppDomain.CurrentDomain.BaseDirectory;
            //        scanner.AssembliesFromPath(location);
            //        scanner.WithDefaultConventions();
            //    }));
            var John = ObjectFactory.GetNamedInstance<IUser>("bdUnit");
            var CentralSleepShop = ObjectFactory.GetNamedInstance<ISleepShop>("bdUnit");
            John.Visit(CentralSleepShop);
            Assert.IsTrue(John.IsDead);
        }
    }
}
