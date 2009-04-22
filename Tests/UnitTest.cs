//#region Using Statements
//using System.Collections.Generic;
//using bdUnit.Interfaces;
//using NUnit.Framework;
//using StructureMap;
//using System;
//#endregion

//namespace bdUnit.Interfaces
//{

//    [PluginFamily("bdUnit")]
//    public interface IUser
//    {
//        IUser Spouse { get; set; }
//        bool IsARunner { get; set; }
//        int Age { get; set; }
//        bool IsDead { get; set; }
//        IList<IUser> Children { get; set; }
//        void Kill(IUser user);
//        void Marry(IUser user);
//        void Visit(ISleepShop sleepshop);
//        void Total();
//    }

//    [PluginFamily("bdUnit")]
//    public interface ISleepShop
//    {
//        ILocation Location { get; set; }
//        bool IsOpen { get; set; }
//        void Locate();
//    }

//    [PluginFamily("bdUnit")]
//    public interface ILocation
//    {
//        decimal Latitude { get; set; }
//        decimal Longitude { get; set; }
//    }
//}

//namespace bdUnit.Tests
//{
//    [TestFixture]
//    public class LogansRun_Marriage
//    {
//        [TestFixtureSetUp]
//        public void Setup()
//        {
//            ObjectFactory.Initialize(
//            x => x.Scan(scanner =>
//            {
//                var location = AppDomain.CurrentDomain.BaseDirectory;
//                scanner.AssembliesFromPath(location);
//                scanner.WithDefaultConventions();
//            }));
//        }

//        [Test]
//        public void When_User_Marry_User()
//        {
//            IUser Peter = ObjectFactory.GetNamedInstance<IUser>("bdUnit");
//            IUser Eve = ObjectFactory.GetNamedInstance<IUser>("bdUnit");
//            Peter.Marry(Eve);
//            Assert.IsTrue(!Peter.IsARunner);
//            Assert.IsTrue(Peter.Age < 30);
//            Assert.IsTrue(Peter.Spouse == Eve);
//            Assert.IsTrue(Eve.Spouse == Peter);
//        }

//        [Test]
//        public void When_User_Kill_User()
//        {
//            IUser a = ObjectFactory.GetNamedInstance<IUser>("bdUnit");
//            IUser b = ObjectFactory.GetNamedInstance<IUser>("bdUnit");
//            a.Kill(b);
//            Assert.IsTrue(b.IsDead);
//            Assert.IsTrue(!a.IsDead);
//        }

//        [Test]
//        public void When_User_Visit_SleepShop()
//        {
//            IUser John = ObjectFactory.GetNamedInstance<IUser>("bdUnit");
//            ISleepShop CentralSleepShop = ObjectFactory.GetNamedInstance<ISleepShop>("bdUnit");
//            John.Visit(CentralSleepShop);
//            Assert.IsTrue(John.IsDead);
//        }
//    }
//}
