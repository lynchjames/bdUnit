using System;
using System.Collections.Generic;
using bdUnit.Interfaces;

namespace MyNewDomain
{
    public class User : IUser
    {
        public void Kill(IUser user)
        {
            throw new NotImplementedException();
        }

        public void ProposeTo(IUser user)
        {
            
        }

        public void Marry(IUser user)
        {
            this.Spouse = user;
            //this.Married = true;
            user.Spouse = this;
            //user.Married = true;
        }

        public void Meet(IList<IUser> user)
        {
            throw new NotImplementedException();
        }

        public void Locate()
        {
            throw new NotImplementedException();
        }

        public void Find()
        {
            throw new NotImplementedException();
        }

        public IUser Spouse { get; set; }
        public string Name { get; set; }
        public bool Married { get; set; }
        public bool IsDead { get; set; }
        public int Age { get; set; }
        public DateTime CreatedDate { get; set; }
        public ILocation Location { get; set; }
        public IList<IUser> Children { get; set; }
    }

    public class SleepShop : ISleepShop
    {
        public void Find()
        {
            throw new NotImplementedException();
        }

        public ILocation Location { get; set; }
        public bool IsOpen { get; set; }
    }

    public class Location : ILocation
    {
        public double Latitude { get; set; }
        public double Longitude { get; set; }
    }
}