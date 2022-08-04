import { Component, OnInit } from '@angular/core';

import { CourseHttpService } from '../course-http.service';
import { Router } from '@angular/router';
import { Course } from '../models';
import { PageEvent } from '@angular/material/paginator';

@Component({
  selector: 'app-courses',
  templateUrl: './courses.component.html',
  styleUrls: ['./courses.component.css']
})
export class CoursesComponent implements OnInit {
  limit: number = 5;
  skip: number = 0;
  courses: Course[] = [];

  count: number = 0;  

  scheduled: string | null = null;
  language: string | null = null;
  search_title: string | null = null;

  constructor(
    private course_http: CourseHttpService,
    private router: Router
  ) { }

  ngOnInit(): void {
    this.getCourses();
  }

  filter(): void {
    this.getCourses();
  }

  getCourses(): void {
    if (this.search_title == '') this.search_title = null;

    let scheduled = null;
    if (this.scheduled == '1') scheduled = true;

    this.course_http.getCourses(this.limit, this.skip, this.search_title, this.language, scheduled).subscribe({
      next: (res: any) => {
        this.courses = res.corsi;
        this.count = res.count;
      }
    })
  }

  onPageChange(pageEvent: PageEvent): void {
    this.limit = pageEvent.pageSize
    this.skip = pageEvent.pageIndex * this.limit;
    this.getCourses();
  }
}
