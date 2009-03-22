using System;
using System.Collections.Generic;
using bdUnit.Interfaces;

namespace MyNewDomain
{
    public class Car 
    {
    }

    public class User : IUser
    {
        public User()
        {

        }

        public void ProposeTo(IUser user)
        {
        }

        public void Find()
        {
            
        }

        public IUser Spouse { get; set; }
        private string _name = "";
        public string Name {
            get { return _name; }
            set
            {
                _name = value;
                this.IsDead = true;
            } }
        public bool IsARunner { get; set; }
        public int Age { get; set; }
        public bool IsDead { get; set; }
        public DateTime CreatedDate { get; set; }
        public IList<IUser> Children { get; set; }
        
        public void Kill(IUser user)
        {
            
        }

        public void Marry(IUser user)
        {
            this.Spouse = user;
            user.Spouse = this;
        }

        public void Meet(IList<IUser> user)
        {
            
        }

        public void Visit(ISleepShop sleepshop)
        {

        }

        public void Total()
        {
            
        }
    }

    public class SleepShop : ISleepShop
    {
        public SleepShop()
        {

        }

        public void Find()
        {
            
        }

        public ILocation Location { get; set; }

        public bool IsOpen { get; set; }

        public void Locate()
        {
            return;
        }
    }

    public class Location222 : ILocation
    {
        public double Latitude { get; set; }

        public double Longitude { get; set; }
    }

    //[Pluggable("bdUnit")]
    //public class Location : ILocationonio
    //{
    //    public decimal Latitude { get; set; }
    //    public decimal Longitude { get; set; }
    //}

    //[Pluggable("bdUnit")]
    //public class Blah : ILocations
    //{
    //    public decimal Latitude { get; set; }
    //    public decimal Longitude { get; set; }
    //}

    //[Pluggable("bdUnit")]
    //public class Woman : IWoman
    //{
    //    public void Kill(IWoman woman)
    //    {
            
    //    }

    //    public void Marry(IWoman woman)
    //    {
            
    //    }

    //    public void Visit(ISleepingShop sleepingshop)
    //    {
            
    //    }

    //    public void Find()
    //    {
            
    //    }

    //    public IWoman Spouse { get; set; }
    //    public bool IsARunner { get; set; }
    //    public int Age { get; set; }
    //    public bool IsDead { get; set; }
    //    public IList<IUser> Children { get; set; }
    //}

    //[Pluggable("bdUnit")]
    //public class Man : IMan
    //{
    //    public void Kill(IMan man)
    //    {
            
    //    }

    //    public void Marry(IMan man)
    //    {
            
    //    }

    //    public void Visit(ISleepyShop sleepyshop)
    //    {
            
    //    }

    //    public void Find()
    //    {
            
    //    }

    //    public IMan Spouse { get; set; }
    //    public bool IsARunner { get; set; }
    //    public int Age { get; set; }
    //    public bool IsDead { get; set; }
    //    public IList<IUser> Children { get; set; }
    //}

    //[Pluggable("bdUnit")]
    //public class Sleep : ISleepingShop
    //{
    //    public void Find()
    //    {
            
    //    }

    //    public ILocations Locations { get; set; }
    //    public bool IsOpen { get; set; }
    //}

    //[Pluggable("bdUnit")]
    //public class Sleeeep : ISleepyShop
    //{
    //    public void Find()
    //    {
            
    //    }

    //    public ILocation Location { get; set; }
    //    public bool IsOpen { get; set; }
    //}
}