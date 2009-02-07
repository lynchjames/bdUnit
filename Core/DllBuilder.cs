using System;
using System.CodeDom.Compiler;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Reflection;
using System.Text;
using bdUnit.Core;
using Core.Enum;
using Microsoft.CSharp;

namespace bdUnit.Core
{
    public class DllBuilder
    {
        private string[] References = new[]
                                          {
                                              "Rhino.Mocks", "nunit.core", "nunit.core.interfaces", "nunit.framework",
                                              "StructureMap"
                                          };
      
        public void CompileDll()//string folderPath)
        {
            var folderPath = @"C:\Development\Example";
            CodeDomProvider compiler = new CSharpCodeProvider(new Dictionary<string, string> {{"CompilerVersion","v3.5"}});
            var compilerParameters = new CompilerParameters
                                         {
                                             GenerateInMemory = false,
                                             GenerateExecutable = false,
                                             IncludeDebugInformation = true,
                                             OutputAssembly = "bdUnit.dll"
                                         };
            foreach (var reference in References)
            {
                compilerParameters.ReferencedAssemblies.Add(AppDomain.CurrentDomain.BaseDirectory + "\\" + string.Format("{0}.dll", reference));
            }
            compilerParameters.ReferencedAssemblies.Add("System.dll");
            var source = GetSource(folderPath, UnitTestFrameworkEnum.NUnit);
            var ass = Assembly.GetExecutingAssembly().Location;
            var results = compiler.CompileAssemblyFromSource(compilerParameters, source);
            Debug.WriteLine(results.PathToAssembly);
            File.Copy(AppDomain.CurrentDomain.BaseDirectory + "\\" + compilerParameters.OutputAssembly, folderPath + "\\" + compilerParameters.OutputAssembly, true);
            //return results.PathToAssembly;
        }

        private string[] GetSource(string folderPath, UnitTestFrameworkEnum framework)
        {
            Directory.SetCurrentDirectory(folderPath);
            var directory = Directory.GetCurrentDirectory();
            var files = Directory.GetFiles(folderPath, "*.input");
            string[] source = new string[files.Length];
            for (var i = 0; i < files.Length; i++)
            {
                var paths = new Dictionary<string, string>();
                paths.Add("input", string.Format("{0}", files[i]));
                paths.Add("grammar", "/Development/bdUnit/Core/Grammar/TestWrapper.mg");
                var parser = new Parser(paths);
                source[i] = parser.Parse(framework);
            }
            Debug.Write(source.ToString());
            return source;
        }

        private string source1 = @"#region Using Statements
using System.Collections.Generic;
sing bdUnit.Interfaces;
using NUnit.Framework;
using Rhino.Mocks;
using StructureMap;
#endregion
namespace bdUnit.Interfaces 
{

    [PluginFamily(""bdUnit"")]
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

    [PluginFamily(""bdUnit"")]
    public interface ISleepShop
    {
        ILocation Location { get; set; }
        bool IsOpen { get; set; }
        void Locate();
    }

    [PluginFamily(""bdUnit"")]
    public interface ILocation
    {
        decimal Latitude { get; set; }
        decimal Longitude { get; set; }
    }
}

namespace bdUnit.Tests 
{
    [TestFixture]
    public class LogansRun_Marriage
    {

        [Test]
        public void When_User_Marry_User()
        {
            IUser Peter = ObjectFactory.GetNamedInstance<IUser>(""bdUnit"");
            IUser Eve = ObjectFactory.GetNamedInstance<IUser>(""bdUnit"");
            Peter.Marry(Eve);
            Assert.IsTrue(!Peter.IsARunner);
            Assert.IsTrue(Peter.Age < 30);
            Assert.IsTrue(Peter.Spouse == Eve);
            Assert.IsTrue(Eve.Spouse == Peter);
        }

        [Test]
        public void When_User_Kill_User()
        {
            IUser a = ObjectFactory.GetNamedInstance<IUser>(""bdUnit"");
            IUser b = ObjectFactory.GetNamedInstance<IUser>(""bdUnit"");
            a.Kill(b);
            Assert.IsTrue(b.IsDead);
            Assert.IsTrue(!a.IsDead);
        }

        [Test]
        public void When_User_Visit_SleepShop()
        {
            IUser John = ObjectFactory.GetNamedInstance<IUser>(""bdUnit"");
            ISleepShop CentralSleepShop = ObjectFactory.GetNamedInstance<ISleepShop>(""bdUnit"");
            John.Visit(CentralSleepShop);
            Assert.IsTrue(John.IsDead);
        }
    }
}
namespace bdUnit.Interfaces 
{

    [PluginFamily(""bdUnit"")]
    public interface ICar
    {
        ICar Spouse { get; set; }
        bool IsARunner { get; set; }
        int Age { get; set; }
        bool IsDead { get; set; }
        IList<IPerson> Children { get; set; }
        void Kill(ICar car);
        void Marry(ICar car);
        void Visit(IGarage garage);
        void Total();
    }

    [PluginFamily(""bdUnit"")]
    public interface IGarage
    {
        IParkingSpot ParkingSpot { get; set; }
        bool IsOpen { get; set; }
        void Locate();
    }

    [PluginFamily(""bdUnit"")]
    public interface IParkingSpot
    {
        decimal Latitude { get; set; }
        decimal Longitude { get; set; }
    }
}

namespace bdUnit.Tests 
{
    [TestFixture]
    public class LogansRun_Biking
    {

        [Test]
        public void When_Car_Marry_Car()
        {
            ICar Peter = ObjectFactory.GetNamedInstance<ICar>(""bdUnit"");
            ICar Eve = ObjectFactory.GetNamedInstance<ICar>(""bdUnit"");
            Peter.Marry(Eve);
            Assert.IsTrue(!Peter.IsARunner);
            Assert.IsTrue(Peter.Age < 30);
            Assert.IsTrue(Peter.Spouse == Eve);
            Assert.IsTrue(Eve.Spouse == Peter);
        }

        [Test]
        public void When_Car_Kill_Car()
        {
            ICar a = ObjectFactory.GetNamedInstance<ICar>(""bdUnit"");
            ICar b = ObjectFactory.GetNamedInstance<ICar>(""bdUnit"");
            a.Kill(b);
            Assert.IsTrue(b.IsDead);
            Assert.IsTrue(!a.IsDead);
        }

        [Test]
        public void When_Car_Visit_Garage()
        {
            ICar John = ObjectFactory.GetNamedInstance<ICar>(""bdUnit"");
            IGarage CentralGarage = ObjectFactory.GetNamedInstance<IGarage>(""bdUnit"");
            John.Visit(CentralGarage);
            Assert.IsTrue(John.IsDead);
        }
    }
}
namespace bdUnit.Interfaces 
{

    [PluginFamily(""bdUnit"")]
    public interface IBike
    {
        IBike Spouse { get; set; }
        bool IsARunner { get; set; }
        int Age { get; set; }
        bool IsDead { get; set; }
        IList<IPerson> Children { get; set; }
        void Kill(IBike bike);
        void Marry(IBike bike);
        void Visit(IBikeRack bikerack);
        void Total();
    }

    [PluginFamily(""bdUnit"")]
    public interface IBikeRack
    {
        IStand Stand { get; set; }
        bool IsOpen { get; set; }
        void Locate();
    }

    [PluginFamily(""bdUnit"")]
    public interface IStand
    {
        decimal Latitude { get; set; }
        decimal Longitude { get; set; }
    }
}

namespace bdUnit.Tests 
{
    [TestFixture]
    public class LogansRun_Driving
    {

        [Test]
        public void When_Bike_Marry_Bike()
        {
            IBike Peter = ObjectFactory.GetNamedInstance<IBike>(""bdUnit"");
            IBike Eve = ObjectFactory.GetNamedInstance<IBike>(""bdUnit"");
            Peter.Marry(Eve);
            Assert.IsTrue(!Peter.IsARunner);
            Assert.IsTrue(Peter.Age < 30);
            Assert.IsTrue(Peter.Spouse == Eve);
            Assert.IsTrue(Eve.Spouse == Peter);
        }

        [Test]
        public void When_Bike_Kill_Bike()
        {
            IBike a = ObjectFactory.GetNamedInstance<IBike>(""bdUnit"");
            IBike b = ObjectFactory.GetNamedInstance<IBike>(""bdUnit"");
            a.Kill(b);
            Assert.IsTrue(b.IsDead);
            Assert.IsTrue(!a.IsDead);
        }

        [Test]
        public void When_Bike_Visit_BikeRack()
        {
            IBike John = ObjectFactory.GetNamedInstance<IBike>(""bdUnit"");
            IBikeRack CentralBikeRack = ObjectFactory.GetNamedInstance<IBikeRack>(""bdUnit"");
            John.Visit(CentralBikeRack);
            Assert.IsTrue(John.IsDead);
        }
    }
}";
    }
}
