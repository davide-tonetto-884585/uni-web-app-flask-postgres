import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CourseScheduleItemComponent } from './course-schedule-item.component';

describe('CourseScheduleItemComponent', () => {
  let component: CourseScheduleItemComponent;
  let fixture: ComponentFixture<CourseScheduleItemComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ CourseScheduleItemComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(CourseScheduleItemComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
