import { TestBed } from '@angular/core/testing';

import { QuestionsHttpService } from './questions-http.service';

describe('QuestionsHttpService', () => {
  let service: QuestionsHttpService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(QuestionsHttpService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
