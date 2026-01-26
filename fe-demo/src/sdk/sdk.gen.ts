// @ts-nocheck

import type { Client, Options as Options2, TDataShape } from './client';
import { client } from './client.gen';
import type {
  GetPageInfo6Data,
  GetPageInfo6Responses,
  GetPageInfoData,
  GetPageInfoErrors,
  GetPageInfoResponses,
  GetSprintsWithDetailData,
  GetSprintsWithDetailResponses,
  GetStoriesWithDetail1Data,
  GetStoriesWithDetail1Responses,
  GetStoriesWithDetail22Data,
  GetStoriesWithDetail22Responses,
  GetStoriesWithDetail2Data,
  GetStoriesWithDetail2Errors,
  GetStoriesWithDetail2Responses,
  GetStoriesWithDetail3Data,
  GetStoriesWithDetail3Responses,
  GetStoriesWithDetailData,
  GetStoriesWithDetailResponses,
  GetTasks2Data,
  GetTasks2Responses,
  GetTasksData,
  GetTasksResponses,
  GetTasksWithDetailData,
  GetTasksWithDetailResponses,
  GetTeamsWithDetail2Data,
  GetTeamsWithDetail2Responses,
  GetTeamsWithDetail3Data,
  GetTeamsWithDetail3Responses,
  GetTeamsWithDetail4Data,
  GetTeamsWithDetail4Responses,
  GetTeamsWithDetail5Data,
  GetTeamsWithDetail5Responses,
  GetTeamsWithDetailData,
  GetTeamsWithDetailOfMultipleLevelData,
  GetTeamsWithDetailOfMultipleLevelResponses,
  GetTeamsWithDetailResponses,
  GetUsersData,
  GetUsersResponses,
  GetUserStatData,
  GetUserStatErrors,
  GetUserStatResponses,
} from './types.gen';

export type Options<
  TData extends TDataShape = TDataShape,
  ThrowOnError extends boolean = boolean,
> = Options2<TData, ThrowOnError> & {
  /**
   * You can provide a client instance returned by `createClient()` instead of
   * individual options. This might be also useful if you want to implement a
   * custom client.
   */
  client?: Client;
  /**
   * You can pass arbitrary values through the `meta` object. This can be
   * used to access values that aren't defined as part of the SDK function.
   */
  meta?: Record<string, unknown>;
};

export class Sample1 {
  /**
   * Get Users
   *
   * 1.1 return list of user
   */
  public static getUsers<ThrowOnError extends boolean = false>(
    options?: Options<GetUsersData, ThrowOnError>,
  ) {
    return (options?.client ?? client).get<
      GetUsersResponses,
      unknown,
      ThrowOnError
    >({ url: '/sample_1/users', ...options });
  }

  /**
   * Get Tasks
   *
   * 1.2 return list of tasks
   */
  public static getTasks<ThrowOnError extends boolean = false>(
    options?: Options<GetTasksData, ThrowOnError>,
  ) {
    return (options?.client ?? client).get<
      GetTasksResponses,
      unknown,
      ThrowOnError
    >({ url: '/sample_1/tasks', ...options });
  }

  /**
   * Get Tasks With Detail
   *
   * 1.3 return list of tasks(user)
   */
  public static getTasksWithDetail<ThrowOnError extends boolean = false>(
    options?: Options<GetTasksWithDetailData, ThrowOnError>,
  ) {
    return (options?.client ?? client).get<
      GetTasksWithDetailResponses,
      unknown,
      ThrowOnError
    >({ url: '/sample_1/tasks-with-detail', ...options });
  }

  /**
   * Get Stories With Detail
   *
   * 1.4 return list of story(task(user))
   */
  public static getStoriesWithDetail<ThrowOnError extends boolean = false>(
    options?: Options<GetStoriesWithDetailData, ThrowOnError>,
  ) {
    return (options?.client ?? client).get<
      GetStoriesWithDetailResponses,
      unknown,
      ThrowOnError
    >({ url: '/sample_1/stories-with-detail', ...options });
  }

  /**
   * Get Sprints With Detail
   *
   * 1.5 return list of sprint(story(task(user)))
   */
  public static getSprintsWithDetail<ThrowOnError extends boolean = false>(
    options?: Options<GetSprintsWithDetailData, ThrowOnError>,
  ) {
    return (options?.client ?? client).get<
      GetSprintsWithDetailResponses,
      unknown,
      ThrowOnError
    >({ url: '/sample_1/sprints-with-detail', ...options });
  }

  /**
   * Get Teams With Detail
   *
   * 1.6 return list of team(sprint(story(task(user))))
   */
  public static getTeamsWithDetail<ThrowOnError extends boolean = false>(
    options?: Options<GetTeamsWithDetailData, ThrowOnError>,
  ) {
    return (options?.client ?? client).get<
      GetTeamsWithDetailResponses,
      unknown,
      ThrowOnError
    >({ url: '/sample_1/teams-with-detail', ...options });
  }

  /**
   * Get Teams With Detail 2
   *
   * 1.7 return list of team(sprint(story(task(user))))
   */
  public static getTeamsWithDetail2<ThrowOnError extends boolean = false>(
    options?: Options<GetTeamsWithDetail2Data, ThrowOnError>,
  ) {
    return (options?.client ?? client).get<
      GetTeamsWithDetail2Responses,
      unknown,
      ThrowOnError
    >({ url: '/sample_1/teams-with-detail2', ...options });
  }
}

export class Sample2 {
  /**
   * Get Teams With Detail
   *
   * 1.1 teams with senior members
   */
  public static getTeamsWithDetail<ThrowOnError extends boolean = false>(
    options?: Options<GetTeamsWithDetail3Data, ThrowOnError>,
  ) {
    return (options?.client ?? client).get<
      GetTeamsWithDetail3Responses,
      unknown,
      ThrowOnError
    >({ url: '/sample_2/teams-with-detail', ...options });
  }

  /**
   * Get Teams With Detail Of Multiple Level
   *
   * 1.2 teams with senior and junior members
   */
  public static getTeamsWithDetailOfMultipleLevel<
    ThrowOnError extends boolean = false,
  >(options?: Options<GetTeamsWithDetailOfMultipleLevelData, ThrowOnError>) {
    return (options?.client ?? client).get<
      GetTeamsWithDetailOfMultipleLevelResponses,
      unknown,
      ThrowOnError
    >({ url: '/sample_2/teams-with-detail-of-multiple-level', ...options });
  }
}

export class Sample3 {
  /**
   * Get Teams With Detail
   *
   * 1.1 expose (provide) ancestor data to descendant node.
   */
  public static getTeamsWithDetail<ThrowOnError extends boolean = false>(
    options?: Options<GetTeamsWithDetail4Data, ThrowOnError>,
  ) {
    return (options?.client ?? client).get<
      GetTeamsWithDetail4Responses,
      unknown,
      ThrowOnError
    >({ url: '/sample_3/teams-with-detail', ...options });
  }
}

export class Sample4 {
  /**
   * Get Teams With Detail
   */
  public static getTeamsWithDetail<ThrowOnError extends boolean = false>(
    options?: Options<GetTeamsWithDetail5Data, ThrowOnError>,
  ) {
    return (options?.client ?? client).get<
      GetTeamsWithDetail5Responses,
      unknown,
      ThrowOnError
    >({ url: '/sample_4/teams-with-detail', ...options });
  }
}

export class Sample5 {
  /**
   * Get Page Info
   */
  public static getPageInfo<ThrowOnError extends boolean = false>(
    options: Options<GetPageInfoData, ThrowOnError>,
  ) {
    return (options.client ?? client).get<
      GetPageInfoResponses,
      GetPageInfoErrors,
      ThrowOnError
    >({ url: '/sample_5/page-info/{team_id}', ...options });
  }
}

export class Sample6 {
  /**
   * Get Page Info 6
   */
  public static getPageInfo6<ThrowOnError extends boolean = false>(
    options?: Options<GetPageInfo6Data, ThrowOnError>,
  ) {
    return (options?.client ?? client).get<
      GetPageInfo6Responses,
      unknown,
      ThrowOnError
    >({ url: '/sample_6/page-info', ...options });
  }
}

export class Sample7 {
  /**
   * Get Tasks
   */
  public static getTasks<ThrowOnError extends boolean = false>(
    options?: Options<GetTasks2Data, ThrowOnError>,
  ) {
    return (options?.client ?? client).get<
      GetTasks2Responses,
      unknown,
      ThrowOnError
    >({ url: '/sample_7/tasks', ...options });
  }

  /**
   * Get User Stat
   */
  public static getUserStat<ThrowOnError extends boolean = false>(
    options: Options<GetUserStatData, ThrowOnError>,
  ) {
    return (options.client ?? client).get<
      GetUserStatResponses,
      GetUserStatErrors,
      ThrowOnError
    >({ url: '/sample_7/user/{id}/stat', ...options });
  }
}

export class Demo {
  /**
   * Get Stories With Detail
   */
  public static getStoriesWithDetail<ThrowOnError extends boolean = false>(
    options: Options<GetStoriesWithDetail2Data, ThrowOnError>,
  ) {
    return (options.client ?? client).post<
      GetStoriesWithDetail2Responses,
      GetStoriesWithDetail2Errors,
      ThrowOnError
    >({
      url: '/demo/stories',
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });
  }

  /**
   * Get Stories With Detail 1
   */
  public static getStoriesWithDetail1<ThrowOnError extends boolean = false>(
    options?: Options<GetStoriesWithDetail1Data, ThrowOnError>,
  ) {
    return (options?.client ?? client).get<
      GetStoriesWithDetail1Responses,
      unknown,
      ThrowOnError
    >({ url: '/demo/stories-1', ...options });
  }

  /**
   * Get Stories With Detail 2
   */
  public static getStoriesWithDetail2<ThrowOnError extends boolean = false>(
    options?: Options<GetStoriesWithDetail22Data, ThrowOnError>,
  ) {
    return (options?.client ?? client).get<
      GetStoriesWithDetail22Responses,
      unknown,
      ThrowOnError
    >({ url: '/demo/stories-2', ...options });
  }

  /**
   * Get Stories With Detail 3
   */
  public static getStoriesWithDetail3<ThrowOnError extends boolean = false>(
    options?: Options<GetStoriesWithDetail3Data, ThrowOnError>,
  ) {
    return (options?.client ?? client).get<
      GetStoriesWithDetail3Responses,
      unknown,
      ThrowOnError
    >({ url: '/demo/stories-3', ...options });
  }
}
