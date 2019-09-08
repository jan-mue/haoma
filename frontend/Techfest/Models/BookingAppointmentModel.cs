using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;

namespace Techfest.Models
{
    public class BookingAppointmentModel
    {
        public string Patient_key { get; set; }

        public string Sex { get; set; }

        public double Height { get; set; }

        public DateTime Birth_date { get; set; }

        public DateTime Procedure_start { get; set; }

        public string Procedure_code { get; set; }
            
        public int Radiologist_id { get; set; }

        public double Weight { get; set; }

        public DateTime Registration_arrival { get; set; }  

        public string Insurance { get; set; }

        public string Technician_id { get; set; }

        public BookingAppointmentModel()
        {

        }
    }
}