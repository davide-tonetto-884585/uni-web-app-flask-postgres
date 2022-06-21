import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { NgCeilPipeModule } from 'angular-pipes';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { UserLoginComponent } from './user-login/user-login.component';
import { StudentSignupComponent } from './student-signup/student-signup.component';

import { UserHttpService } from './user-http.service';
import { ActivateProfileComponent } from './activate-profile/activate-profile.component';
import { HomeComponent } from './home/home.component';
import { TopBarComponent } from './top-bar/top-bar.component';
import { CourseCardComponent } from './course-card/course-card.component';
import { CarouselComponent } from './carousel/carousel.component';
import { CarouselItemComponent } from './carousel-item/carousel-item.component';
import { CoursesComponent } from './courses/courses.component';
import { CourseDetailComponent } from './course-detail/course-detail.component';

@NgModule({
  declarations: [
    AppComponent,
    UserLoginComponent,
    StudentSignupComponent,
    ActivateProfileComponent,
    HomeComponent,
    TopBarComponent,
    CourseCardComponent,
    CarouselComponent,
    CarouselItemComponent,
    CoursesComponent,
    CourseDetailComponent
  ],
  imports: [
    FormsModule,
    HttpClientModule,
    BrowserModule,
    AppRoutingModule,
    NgCeilPipeModule
  ],
  providers: [
    { provide: UserHttpService, useClass: UserHttpService }
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
