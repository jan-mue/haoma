using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Net.Http;
using System.Net.Mail;
using System.Threading.Tasks;
using System.Web;
using System.Web.Mvc;
using Techfest.Helpers;
using Techfest.Models;

namespace Techfest.Controllers
{
    public class AppointmentController : Controller
    {
        public ActionResult Index()
        {
            return View(new BookingAppointmentModel());
        }

        [HttpPost]
        public ActionResult AddAppointment(BookingAppointmentModel model)
        {
            SendEmail();
            return null;
        }

        [HttpGet]
        public ActionResult FindPatientsByID(string id)
        {
            HttpBuilder builder = new HttpBuilder();
            string jsonResponse = builder.GetResponse(id.ToString());
            BookingAppointmentModel model = JsonConvert.DeserializeObject<BookingAppointmentModel>(jsonResponse);
            return View("~/Views/Appointment/Index.cshtml", model);
        }

        [HttpGet]
        public ActionResult FindPatientReport()
        {
            return null;
        }

        private static void SendEmail()
        {
            var fromAddress = new MailAddress("techfestmunich2019@gmail.com", "Techfest");
            var toAddress = new MailAddress("nele.nasa@gmail.com", "Nenad");
            const string fromPassword = "TechFestMunich2019";
            const string subject = "Link to your recent application";
            string body = $"Respected,{Environment.NewLine}Your doctor has booked you an appointment.Follow the link we are sending you for more information.{Environment.NewLine}" +
                $"https://localhost:44330/appointment/info" +
                $"Kind regards,{Environment.NewLine}" +
                $"Elon Musk.";

            var smtp = new SmtpClient
            {
                Host = "smtp.gmail.com",
                Port = 587,
                EnableSsl = true,
                DeliveryMethod = SmtpDeliveryMethod.Network,
                UseDefaultCredentials = false,
                Credentials = new NetworkCredential(fromAddress.Address, fromPassword)
            };
            using (var message = new MailMessage(fromAddress, toAddress)
            {
                Subject = subject,
                Body = body
            })
            {
                smtp.Send(message);
            }
        }
    }
}