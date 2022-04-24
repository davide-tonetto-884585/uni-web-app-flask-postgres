import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { UserLoginComponent } from './user-login/user-login.component';
import { StudentSignupComponent } from './student-signup/student-signup.component';

const routes: Routes = [
  { path: '', redirectTo: '/login', pathMatch: 'full' },
{ path: 'login', component: UserLoginComponent },
{ path: 'signup', component: StudentSignupComponent }];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
