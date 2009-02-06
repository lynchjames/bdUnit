#region Using Statements
using System.Collections.Generic;
using bdUnit.Interfaces;
using NUnit.Framework;
using Rhino.Mocks;
#endregion

namespace bdUnit.Interfaces
{

    public interface IUser
    {
        IUser Spouse { get; set; }
        bool IsARunner { get; set; }
        int Age { get; set; }
        bool IsDead { get; set; }
        IList<IPerson> Children { get; set; }
        void Kill(IUser user1);
        void Marry(IUser user2);
        void Visit(ISleepShop sleepshop3);
        void Total();
    }

    public interface ISleepShop
    {
        //ILocation Location { get; set; }
        bool IsOpen { get; set; }
        void Locate();
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
            var mocks = new MockRepository();
            IUser Peter = (IUser)mocks.Stub(typeof(IUser));
            IUser Eve = (IUser)mocks.Stub(typeof(IUser));
            Peter.Marry(Eve);
            Assert.IsTrue(Peter.IsARunner == false);
            Assert.IsTrue(Peter.Age < 30);
            Assert.IsTrue(Peter.Spouse == Eve);
            Assert.IsTrue(Eve.Spouse == Peter);
        }

        [Test]
        public void When_User_Kill_User()
        {
            var mocks = new MockRepository();
            IUser a = (IUser)mocks.Stub(typeof(IUser));
            IUser b = (IUser)mocks.Stub(typeof(IUser));
            a.Kill(b);
            Assert.IsTrue(b.IsDead == true);
            Assert.IsTrue(a.IsDead == false);
        }

        [Test]
        public void When_User_Visit_SleepShop()
        {
            var mocks = new MockRepository();
            IUser John = (IUser)mocks.Stub(typeof(IUser));
            ISleepShop CentralSleepShop = (ISleepShop)mocks.Stub(typeof(ISleepShop));
            John.Visit(CentralSleepShop);
            Assert.IsTrue(John.IsDead == true);
        }
    }
}