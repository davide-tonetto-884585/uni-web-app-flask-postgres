import { TestBed } from '@angular/core/testing';

import { StatisticsHttpService } from './statistics-http.service';

describe('StatisticsHttpService', () => {
  let service: StatisticsHttpService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(StatisticsHttpService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
