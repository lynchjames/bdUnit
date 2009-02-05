#region Using Statements

using System.Collections.Generic;
using NUnit.Framework;

#endregion

namespace bdUnit.ExampleUnitTests
{
    [TestFixture]
    public class Test_LogansRun_Setup
    {
        //Match --I want a User to have a FirstName and a LastName and a UserName and an Age (1..100) and a MarriedTo and an IsMarried (true|false)--
        public class User
        {
            public string UserName { get; set; }
            public int Age { get; set; }
            public string FirstName { get; set; }
            public string LastName { get; set; }
            public User MarriedTo { get; set; }
            public bool IsMarried { get; set; }
            public bool IsDead { get; set; }

            //Match -- I want a User to be able to Marry another User and when a User Marry another User, each User should be marriedto the other User's firstname and lastname and yes ismarried
            public void Marry(User user)
            {
            }
        }

        public static User userA = new User
                                       {
                                           Age = 20,
                                           FirstName = "Steve",
                                           IsMarried = true,
                                           LastName = "Jobs",
                                           UserName = "stevo"
                                       };

        public static User userB = new User
                                       {
                                           Age = 25,
                                           FirstName = "Janice",
                                           IsMarried = true,
                                           LastName = "Smith",
                                           UserName = "jan10"
                                       };

        [Test]
        public void Test_LogansRun()
        {
            var users = new List<User> {userA, userB};
            var count = users.Count;
            //Match -- each User's username should be unique
            for (var i = 0; i < count; i++)
            {
                var user1 = users[i];
                for (var j = 0; j < count; j++)
                {
                    var user2 = users[j];
                    if (i != j)
                    {
                        Assert.IsFalse(user1.UserName == user2.UserName);
                    }
                }
            }

            //Test the Method
            userA.Marry(userB);
            Assert.IsTrue(userA.LastName == userB.LastName);
            Assert.IsTrue(userA.MarriedTo == userB);
            Assert.IsTrue(userB.MarriedTo == userA);
            Assert.IsTrue(userA.IsMarried && userB.IsMarried);

            //Match -- each user's age should be less than 30
            for (var i = 0; i < count; i++)
            {
                Assert.IsTrue(users[i].Age < 30);
            }
        }
    }
}