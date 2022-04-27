import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { UserLoginComponent } from './user-login/user-login.component';
import { StudentSignupComponent } from './student-signup/student-signup.component';

import { UserHttpService } from './user-http.service';

@NgModule({
  declarations: [
    AppComponent,
    UserLoginComponent,
    StudentSignupComponent
  ],
  imports: [
    FormsModule, 
    HttpClientModule,
    BrowserModule,
    AppRoutingModule
  ],
  providers: [
    {provide: UserHttpService, useClass: UserHttpService }
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
