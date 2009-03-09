//#region Using Statements
//using System.Collections.Generic;
//using System.Diagnostics;
//using bdUnit.Interfaces;
//using NUnit.Framework;
//using StructureMap;
//using System;
//#endregion

//namespace bdUnit.Interfaces
//{

//    [PluginFamily("bdUnit")]
//    public partial interface IUser
//    {
//        IUser Spouse { get; set; }
//        string Name { get; set; }
//        bool IsARunner { get; set; }
//        int Age { get; set; }
//        DateTime IsDead { get; set; }
//        IList<IUser> Children { get; set; }
//        void Kill(IUser user);
//        void Marry(IUser user);
//        void Visit(ISleepShop sleepshop);
//        void Find();
//    }

//    [PluginFamily("bdUnit")]
//    public partial interface ISleepShop
//    {
//        ILocation Location { get; set; }
//        bool IsOpen { get; set; }
//        void Find();
//    }

//    [PluginFamily("bdUnit")]
//    public partial interface ILocation
//    {
//        decimal Latitude { get; set; }
//        decimal Longitude { get; set; }
//    }
//}

//namespace bdUnit.Tests
//{
//    [TestFixture]
//    public class LogansRun
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
//            Debug.WriteLine("Assert.IsTrue(!Peter.IsARunner);");
//            Assert.IsTrue(!Peter.IsARunner);
//            Debug.WriteLine("Assert.IsTrue(Peter.Age < 21);");
//            Assert.IsTrue(Peter.Age < 21);
//            Debug.WriteLine("Assert.IsTrue(Peter.Spouse == Eve);Assert.IsTrue(Eve.Spouse == Peter);");
//            Assert.IsTrue(Peter.Spouse == Eve);
//            Assert.IsTrue(Eve.Spouse == Peter);
//        }

//        [Test]
//        public void When_User_Name_Is_Set()
//        {
//            IUser a = ObjectFactory.GetNamedInstance<IUser>("bdUnit");
//            a.Name = "kjh";
//            Debug.WriteLine("Assert.IsTrue(a.IsDead);");

//            Debug.WriteLine("var dateTime1 = DateTime.Parse(\"22/04/1983\");");
//            var dateTime1 = DateTime.Parse("22/04/1983");
//            Debug.WriteLine("Assert.IsTrue(a.IsDead < dateTime1);");
//            Assert.IsTrue(a.IsDead < dateTime1);
//        }

//        [Test]
//        public void When_User_Visit_SleepShop()
//        {
//            IUser John = ObjectFactory.GetNamedInstance<IUser>("bdUnit");
//            ISleepShop CentralSleepShop = ObjectFactory.GetNamedInstance<ISleepShop>("bdUnit");
//            John.Visit(CentralSleepShop);
//            Debug.WriteLine("Assert.IsTrue(John.IsDead);");
//            Assert.IsTrue(John.IsDead);
//        }
//    }
//}