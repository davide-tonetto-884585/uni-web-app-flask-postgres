import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { UserLoginComponent } from './user-login/user-login.component';
import { StudentSignupComponent } from './student-signup/student-signup.component';
import { ActivateProfileComponent } from './activate-profile/activate-profile.component';
import { HomeComponent } from './home/home.component';
import { CoursesComponent } from './courses/courses.component';
import { CourseDetailComponent } from './course-detail/course-detail.component';
import { MyCoursesComponent } from './my-courses/my-courses.component';
import { TeacherSignupComponent } from './teacher-signup/teacher-signup.component';
import { TeacherPageComponent } from './teacher-page/teacher-page.component';

const routes: Routes = [
  { path: '', redirectTo: '/home', pathMatch: 'full' },
  { path: 'home', component: HomeComponent},
  { path: 'login', component: UserLoginComponent },
  { path: 'signup', component: StudentSignupComponent },
  { path: 'teacherSignup', component: TeacherSignupComponent },
  { path: 'activate/:category/:token/:user_id', component: ActivateProfileComponent },
  { path: 'courses', component: CoursesComponent },
  { path: 'course/:id', component: CourseDetailComponent },
  { path: 'myCourses', component: MyCoursesComponent },
  { path: 'teacher/:id', component: TeacherPageComponent }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
