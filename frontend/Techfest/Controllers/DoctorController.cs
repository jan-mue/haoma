using System.Web.Mvc;

namespace Techfest.Controllers
{
    [RoutePrefix("Doctor")]
    public class DoctorController : Controller
    {
        public ActionResult DoctorView()
        {
            return PartialView("~/Views/Doctor/_Doctor.cshtml");
        }
    }
}