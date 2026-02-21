// @ts-nocheck

export type ClientOptions = {
    baseUrl: 'http://localhost:8001' | (string & {});
};

/**
 * HTTPValidationError
 */
export type HttpValidationError = {
    /**
     * Detail
     */
    detail?: Array<ValidationError>;
};

/**
 * Payload
 */
export type Payload = {
    /**
     * Message
     */
    message?: string;
    /**
     * Name
     */
    name: string;
};

/**
 * Sample1SprintDetail
 */
export type Sample1SprintDetail = {
    /**
     * Id
     */
    id: number;
    /**
     * Name
     */
    name: string;
    /**
     * Status
     */
    status: string;
    /**
     * Team Id
     */
    team_id: number;
    /**
     * Stories
     */
    stories: Array<Sample1StoryDetail>;
};

/**
 * Sample1StoryDetail
 */
export type Sample1StoryDetail = {
    /**
     * Id
     */
    id: number;
    /**
     * Name
     */
    name: string;
    /**
     * Owner Id
     */
    owner_id: number;
    /**
     * Sprint Id
     */
    sprint_id: number;
    /**
     * Tasks
     */
    tasks: Array<Sample1TaskDetail>;
    owner: User | null;
};

/**
 * Sample1TaskDetail
 */
export type Sample1TaskDetail = {
    /**
     * Id
     */
    id: number;
    /**
     * Name
     */
    name: string;
    /**
     * Owner Id
     */
    owner_id: number;
    /**
     * Story Id
     */
    story_id: number;
    /**
     * Estimate
     */
    estimate: number;
    user: User | null;
};

/**
 * Sample1TeamDetail
 */
export type Sample1TeamDetail = {
    /**
     * Id
     */
    id: number;
    /**
     * Name
     */
    name: string;
    /**
     * Sprints
     */
    sprints: Array<Sample1SprintDetail>;
    /**
     * Members
     */
    members: Array<User>;
};

/**
 * Sample1TeamDetail2
 */
export type Sample1TeamDetail2 = {
    /**
     * Id
     */
    id: number;
    /**
     * Name
     */
    name: string;
    /**
     * Sprints
     */
    sprints: Array<Sample1SprintDetail>;
    /**
     * Members
     */
    members: Array<User>;
};

/**
 * Sample2TeamDetail
 */
export type Sample2TeamDetail = {
    /**
     * Id
     */
    id: number;
    /**
     * Name
     */
    name: string;
    /**
     * Senior Members
     */
    senior_members: Array<User>;
};

/**
 * Sample2TeamDetailMultipleLevel
 */
export type Sample2TeamDetailMultipleLevel = {
    /**
     * Id
     */
    id: number;
    /**
     * Name
     */
    name: string;
    /**
     * Senior Members
     */
    senior_members: Array<User>;
    /**
     * Junior Members
     */
    junior_members: Array<User>;
    /**
     * Senior Junior
     */
    senior_junior: Array<User>;
};

/**
 * Sample3SprintDetail
 */
export type Sample3SprintDetail = {
    /**
     * Id
     */
    id: number;
    /**
     * Name
     */
    name: string;
    /**
     * Status
     */
    status: string;
    /**
     * Team Id
     */
    team_id: number;
    /**
     * Stories
     */
    stories: Array<Sample3StoryDetail>;
};

/**
 * Sample3StoryDetail
 */
export type Sample3StoryDetail = {
    /**
     * Id
     */
    id: number;
    /**
     * Name
     */
    name: string;
    /**
     * Owner Id
     */
    owner_id: number;
    /**
     * Sprint Id
     */
    sprint_id: number;
    /**
     * Tasks
     */
    tasks: Array<Sample3TaskDetail>;
};

/**
 * Sample3TaskDetail
 */
export type Sample3TaskDetail = {
    /**
     * Id
     */
    id: number;
    /**
     * Name
     */
    name: string;
    /**
     * Owner Id
     */
    owner_id: number;
    /**
     * Story Id
     */
    story_id: number;
    /**
     * Estimate
     */
    estimate: number;
    user: User | null;
    /**
     * Full Name
     */
    full_name: string;
};

/**
 * Sample3TeamDetail
 */
export type Sample3TeamDetail = {
    /**
     * Id
     */
    id: number;
    /**
     * Name
     */
    name: string;
    /**
     * Sprints
     */
    sprints: Array<Sample3SprintDetail>;
};

/**
 * Sample4SprintDetail
 */
export type Sample4SprintDetail = {
    /**
     * Id
     */
    id: number;
    /**
     * Name
     */
    name: string;
    /**
     * Status
     */
    status: string;
    /**
     * Team Id
     */
    team_id: number;
    /**
     * Stories
     */
    stories?: Array<Sample4StoryDetail>;
    /**
     * Task Count
     */
    task_count?: number;
};

/**
 * Sample4StoryDetail
 */
export type Sample4StoryDetail = {
    /**
     * Id
     */
    id: number;
    /**
     * Name
     */
    name: string;
    /**
     * Owner Id
     */
    owner_id: number;
    /**
     * Sprint Id
     */
    sprint_id: number;
    /**
     * Tasks
     */
    tasks?: Array<Sample4TaskDetail>;
    /**
     * Task Count
     */
    task_count?: number;
};

/**
 * Sample4TaskDetail
 */
export type Sample4TaskDetail = {
    /**
     * Id
     */
    id: number;
    /**
     * Name
     */
    name: string;
    /**
     * Owner Id
     */
    owner_id: number;
    /**
     * Story Id
     */
    story_id: number;
    /**
     * Estimate
     */
    estimate: number;
    user?: User | null;
};

/**
 * Sample4TeamDetail
 */
export type Sample4TeamDetail = {
    /**
     * Id
     */
    id: number;
    /**
     * Name
     */
    name: string;
    /**
     * Sprints
     */
    sprints: Array<Sample4SprintDetail>;
    /**
     * Task Count
     */
    task_count: number;
    /**
     * Total Task Count
     */
    total_task_count: number;
    /**
     * Description
     */
    description: string;
};

/**
 * Sample5Root
 */
export type Sample5Root = {
    /**
     * Summary
     */
    summary: string;
    team: Sample5TeamDetail | null;
};

/**
 * Sample5SprintDetail
 */
export type Sample5SprintDetail = {
    /**
     * Id
     */
    id: number;
    /**
     * Name
     */
    name: string;
    /**
     * Status
     */
    status: string;
    /**
     * Team Id
     */
    team_id: number;
    /**
     * Stories
     */
    stories: Array<Sample5StoryDetail>;
    /**
     * Task Count
     */
    task_count: number;
};

/**
 * Sample5StoryDetail
 */
export type Sample5StoryDetail = {
    /**
     * Id
     */
    id: number;
    /**
     * Name
     */
    name: string;
    /**
     * Owner Id
     */
    owner_id: number;
    /**
     * Sprint Id
     */
    sprint_id: number;
    /**
     * Tasks
     */
    tasks: Array<Sample5TaskDetail>;
    /**
     * Task Count
     */
    task_count: number;
};

/**
 * Sample5TaskDetail
 */
export type Sample5TaskDetail = {
    /**
     * Id
     */
    id: number;
    /**
     * Name
     */
    name: string;
    /**
     * Owner Id
     */
    owner_id: number;
    /**
     * Story Id
     */
    story_id: number;
    /**
     * Estimate
     */
    estimate: number;
    user: User | null;
};

/**
 * Sample5TeamDetail
 */
export type Sample5TeamDetail = {
    /**
     * Id
     */
    id: number;
    /**
     * Name
     */
    name: string;
    /**
     * Sprints
     */
    sprints: Array<Sample5SprintDetail>;
    /**
     * Task Count
     */
    task_count: number;
    /**
     * Description
     */
    description: string;
};

/**
 * Sample6Root
 */
export type Sample6Root = {
    /**
     * Summary
     */
    summary: string;
    /**
     * Teams
     */
    teams: Array<Sample6TeamDetail>;
};

/**
 * Sample6SprintDetail
 */
export type Sample6SprintDetail = {
    /**
     * Name
     */
    name: string;
    /**
     * Stories
     */
    stories: Array<Sample6StoryDetail>;
};

/**
 * Sample6StoryDetail
 */
export type Sample6StoryDetail = {
    /**
     * Name
     */
    name: string;
    /**
     * Tasks
     */
    tasks: Array<Sample6TaskDetail>;
};

/**
 * Sample6TaskDetail
 */
export type Sample6TaskDetail = {
    /**
     * Name
     */
    name: string;
    user: User | null;
};

/**
 * Sample6TeamDetail
 */
export type Sample6TeamDetail = {
    /**
     * Name
     */
    name: string;
    /**
     * Sprints
     */
    sprints: Array<Sample6SprintDetail>;
};

/**
 * Sample7SprintDetail
 */
export type Sample7SprintDetail = {
    /**
     * Id
     */
    id: number;
    /**
     * Name
     */
    name: string;
    /**
     * Status
     */
    status: string;
    /**
     * Team Id
     */
    team_id: number;
    /**
     * Stories
     */
    stories: Array<Story>;
};

/**
 * Sample7TaskDetail
 */
export type Sample7TaskDetail = {
    /**
     * Id
     */
    id: number;
    /**
     * Name
     */
    name: string;
    /**
     * Owner Id
     */
    owner_id: number;
    /**
     * Story Id
     */
    story_id: number;
    /**
     * Estimate
     */
    estimate: number;
    user: User | null;
};

/**
 * Sample7TeamDetail
 */
export type Sample7TeamDetail = {
    /**
     * Id
     */
    id: number;
    /**
     * Name
     */
    name: string;
    /**
     * Sprints
     */
    sprints: Array<Sample7SprintDetail>;
};

/**
 * Story
 */
export type Story = {
    /**
     * Id
     */
    id: number;
    /**
     * Name
     */
    name: string;
    /**
     * Owner Id
     */
    owner_id: number;
    /**
     * Sprint Id
     */
    sprint_id: number;
};

/**
 * Story0
 */
export type Story0 = {
    /**
     * Id
     */
    id: number;
    /**
     * Name
     */
    name: string;
    /**
     * Owner Id
     */
    owner_id: number;
    /**
     * Sprint Id
     */
    sprint_id: number;
    /**
     * Tasks
     */
    tasks: Array<Task0>;
    assignee: User | null;
};

/**
 * Story1
 */
export type Story1 = {
    /**
     * Id
     */
    id: number;
    /**
     * Name
     */
    name: string;
    /**
     * Owner Id
     */
    owner_id: number;
    /**
     * Tasks
     */
    tasks: Array<Task1>;
    assignee: User | null;
    /**
     * Related Users
     */
    related_users: Array<User>;
};

/**
 * Story2
 */
export type Story2 = {
    /**
     * Id
     */
    id: number;
    /**
     * Name
     */
    name: string;
    /**
     * Owner Id
     */
    owner_id: number;
    /**
     * Tasks
     */
    tasks: Array<Task2>;
    assignee: User | null;
    /**
     * Total Estimate
     */
    total_estimate: number;
};

/**
 * Story3
 */
export type Story3 = {
    /**
     * Id
     */
    id: number;
    /**
     * Name
     */
    name: string;
    /**
     * Owner Id
     */
    owner_id: number;
    /**
     * Tasks
     */
    tasks: Array<Task3>;
    assignee: User | null;
};

/**
 * Task
 */
export type Task = {
    /**
     * Id
     */
    id: number;
    /**
     * Name
     */
    name: string;
    /**
     * Owner Id
     */
    owner_id: number;
    /**
     * Story Id
     */
    story_id: number;
    /**
     * Estimate
     */
    estimate: number;
};

/**
 * Task0
 */
export type Task0 = {
    /**
     * Id
     */
    id: number;
    /**
     * Name
     */
    name: string;
    /**
     * Owner Id
     */
    owner_id: number;
    /**
     * Story Id
     */
    story_id: number;
    /**
     * Estimate
     */
    estimate: number;
    user: User | null;
};

/**
 * Task1
 */
export type Task1 = {
    /**
     * Id
     */
    id: number;
    /**
     * Name
     */
    name: string;
    /**
     * Owner Id
     */
    owner_id: number;
    /**
     * Story Id
     */
    story_id: number;
    /**
     * Estimate
     */
    estimate: number;
    user: User | null;
};

/**
 * Task2
 */
export type Task2 = {
    /**
     * Id
     */
    id: number;
    /**
     * Name
     */
    name: string;
    /**
     * Owner Id
     */
    owner_id: number;
    /**
     * Story Id
     */
    story_id: number;
    /**
     * Estimate
     */
    estimate: number;
    user: User | null;
};

/**
 * Task3
 */
export type Task3 = {
    /**
     * Id
     */
    id: number;
    /**
     * Name
     */
    name: string;
    /**
     * Owner Id
     */
    owner_id: number;
    /**
     * Story Id
     */
    story_id: number;
    /**
     * Estimate
     */
    estimate: number;
    user: User | null;
    /**
     * Fullname
     */
    fullname: string;
};

/**
 * User
 */
export type User = {
    /**
     * Id
     */
    id: number;
    /**
     * Name
     */
    name: string;
    /**
     * Level
     */
    level: string;
};

/**
 * ValidationError
 */
export type ValidationError = {
    /**
     * Location
     */
    loc: Array<string | number>;
    /**
     * Message
     */
    msg: string;
    /**
     * Error Type
     */
    type: string;
};

export type GetUsersData = {
    body?: never;
    path?: never;
    query?: never;
    url: '/sample_1/users';
};

export type GetUsersResponses = {
    /**
     * Response Get Users Sample 1 Users Get
     *
     * Successful Response
     */
    200: Array<User>;
};

export type GetUsersResponse = GetUsersResponses[keyof GetUsersResponses];

export type GetTasksData = {
    body?: never;
    path?: never;
    query?: never;
    url: '/sample_1/tasks';
};

export type GetTasksResponses = {
    /**
     * Response Get Tasks Sample 1 Tasks Get
     *
     * Successful Response
     */
    200: Array<Task>;
};

export type GetTasksResponse = GetTasksResponses[keyof GetTasksResponses];

export type GetTasksWithDetailData = {
    body?: never;
    path?: never;
    query?: never;
    url: '/sample_1/tasks-with-detail';
};

export type GetTasksWithDetailResponses = {
    /**
     * Response Get Tasks With Detail Sample 1 Tasks With Detail Get
     *
     * Successful Response
     */
    200: Array<Sample1TaskDetail>;
};

export type GetTasksWithDetailResponse = GetTasksWithDetailResponses[keyof GetTasksWithDetailResponses];

export type GetStoriesWithDetailData = {
    body?: never;
    path?: never;
    query?: never;
    url: '/sample_1/stories-with-detail';
};

export type GetStoriesWithDetailResponses = {
    /**
     * Response Get Stories With Detail Sample 1 Stories With Detail Get
     *
     * Successful Response
     */
    200: Array<Sample1StoryDetail>;
};

export type GetStoriesWithDetailResponse = GetStoriesWithDetailResponses[keyof GetStoriesWithDetailResponses];

export type GetSprintsWithDetailData = {
    body?: never;
    path?: never;
    query?: never;
    url: '/sample_1/sprints-with-detail';
};

export type GetSprintsWithDetailResponses = {
    /**
     * Response Get Sprints With Detail Sample 1 Sprints With Detail Get
     *
     * Successful Response
     */
    200: Array<Sample1SprintDetail>;
};

export type GetSprintsWithDetailResponse = GetSprintsWithDetailResponses[keyof GetSprintsWithDetailResponses];

export type GetTeamsWithDetailData = {
    body?: never;
    path?: never;
    query?: never;
    url: '/sample_1/teams-with-detail';
};

export type GetTeamsWithDetailResponses = {
    /**
     * Response Get Teams With Detail Sample 1 Teams With Detail Get
     *
     * Successful Response
     */
    200: Array<Sample1TeamDetail>;
};

export type GetTeamsWithDetailResponse = GetTeamsWithDetailResponses[keyof GetTeamsWithDetailResponses];

export type GetTeamsWithDetail2Data = {
    body?: never;
    path?: never;
    query?: never;
    url: '/sample_1/teams-with-detail2';
};

export type GetTeamsWithDetail2Responses = {
    /**
     * Response Get Teams With Detail 2 Sample 1 Teams With Detail2 Get
     *
     * Successful Response
     */
    200: Array<Sample1TeamDetail2>;
};

export type GetTeamsWithDetail2Response = GetTeamsWithDetail2Responses[keyof GetTeamsWithDetail2Responses];

export type GetTeamsWithDetail3Data = {
    body?: never;
    path?: never;
    query?: never;
    url: '/sample_2/teams-with-detail';
};

export type GetTeamsWithDetail3Responses = {
    /**
     * Response Get Teams With Detail Sample 2 Teams With Detail Get
     *
     * Successful Response
     */
    200: Array<Sample2TeamDetail>;
};

export type GetTeamsWithDetail3Response = GetTeamsWithDetail3Responses[keyof GetTeamsWithDetail3Responses];

export type GetTeamsWithDetailOfMultipleLevelData = {
    body?: never;
    path?: never;
    query?: never;
    url: '/sample_2/teams-with-detail-of-multiple-level';
};

export type GetTeamsWithDetailOfMultipleLevelResponses = {
    /**
     * Response Get Teams With Detail Of Multiple Level Sample 2 Teams With Detail Of Multiple Level Get
     *
     * Successful Response
     */
    200: Array<Sample2TeamDetailMultipleLevel>;
};

export type GetTeamsWithDetailOfMultipleLevelResponse = GetTeamsWithDetailOfMultipleLevelResponses[keyof GetTeamsWithDetailOfMultipleLevelResponses];

export type GetTeamsWithDetail4Data = {
    body?: never;
    path?: never;
    query?: never;
    url: '/sample_3/teams-with-detail';
};

export type GetTeamsWithDetail4Responses = {
    /**
     * Response Get Teams With Detail Sample 3 Teams With Detail Get
     *
     * Successful Response
     */
    200: Array<Sample3TeamDetail>;
};

export type GetTeamsWithDetail4Response = GetTeamsWithDetail4Responses[keyof GetTeamsWithDetail4Responses];

export type GetTeamsWithDetail5Data = {
    body?: never;
    path?: never;
    query?: never;
    url: '/sample_4/teams-with-detail';
};

export type GetTeamsWithDetail5Responses = {
    /**
     * Response Get Teams With Detail Sample 4 Teams With Detail Get
     *
     * Successful Response
     */
    200: Array<Sample4TeamDetail>;
};

export type GetTeamsWithDetail5Response = GetTeamsWithDetail5Responses[keyof GetTeamsWithDetail5Responses];

export type GetPageInfoData = {
    body?: never;
    path: {
        /**
         * Team Id
         */
        team_id: number;
    };
    query?: never;
    url: '/sample_5/page-info/{team_id}';
};

export type GetPageInfoErrors = {
    /**
     * Validation Error
     */
    422: HttpValidationError;
};

export type GetPageInfoError = GetPageInfoErrors[keyof GetPageInfoErrors];

export type GetPageInfoResponses = {
    /**
     * Successful Response
     */
    200: Sample5Root;
};

export type GetPageInfoResponse = GetPageInfoResponses[keyof GetPageInfoResponses];

export type GetPageInfo6Data = {
    body?: never;
    path?: never;
    query?: never;
    url: '/sample_6/page-info';
};

export type GetPageInfo6Responses = {
    /**
     * Successful Response
     */
    200: Sample6Root;
};

export type GetPageInfo6Response = GetPageInfo6Responses[keyof GetPageInfo6Responses];

export type GetTasks2Data = {
    body?: never;
    path?: never;
    query?: never;
    url: '/sample_7/tasks';
};

export type GetTasks2Responses = {
    /**
     * Response Get Tasks Sample 7 Tasks Get
     *
     * Successful Response
     */
    200: Array<Sample7TaskDetail>;
};

export type GetTasks2Response = GetTasks2Responses[keyof GetTasks2Responses];

export type GetUserStatData = {
    body?: never;
    path: {
        /**
         * Id
         */
        id: number;
    };
    query?: never;
    url: '/sample_7/user/{id}/stat';
};

export type GetUserStatErrors = {
    /**
     * Validation Error
     */
    422: HttpValidationError;
};

export type GetUserStatError = GetUserStatErrors[keyof GetUserStatErrors];

export type GetUserStatResponses = {
    /**
     * Response Get User Stat Sample 7 User  Id  Stat Get
     *
     * Successful Response
     */
    200: Array<Sample7TeamDetail>;
};

export type GetUserStatResponse = GetUserStatResponses[keyof GetUserStatResponses];

export type GetStoriesWithDetail2Data = {
    body: Payload;
    path?: never;
    query?: never;
    url: '/demo/stories';
};

export type GetStoriesWithDetail2Errors = {
    /**
     * Validation Error
     */
    422: HttpValidationError;
};

export type GetStoriesWithDetail2Error = GetStoriesWithDetail2Errors[keyof GetStoriesWithDetail2Errors];

export type GetStoriesWithDetail2Responses = {
    /**
     * Response Get Stories With Detail Demo Stories Post
     *
     * Successful Response
     */
    200: Array<Story0>;
};

export type GetStoriesWithDetail2Response = GetStoriesWithDetail2Responses[keyof GetStoriesWithDetail2Responses];

export type GetStoriesWithDetail1Data = {
    body?: never;
    path?: never;
    query?: never;
    url: '/demo/stories-1';
};

export type GetStoriesWithDetail1Responses = {
    /**
     * Response Get Stories With Detail 1 Demo Stories 1 Get
     *
     * Successful Response
     */
    200: Array<Story1>;
};

export type GetStoriesWithDetail1Response = GetStoriesWithDetail1Responses[keyof GetStoriesWithDetail1Responses];

export type GetStoriesWithDetail22Data = {
    body?: never;
    path?: never;
    query?: never;
    url: '/demo/stories-2';
};

export type GetStoriesWithDetail22Responses = {
    /**
     * Response Get Stories With Detail 2 Demo Stories 2 Get
     *
     * Successful Response
     */
    200: Array<Story2>;
};

export type GetStoriesWithDetail22Response = GetStoriesWithDetail22Responses[keyof GetStoriesWithDetail22Responses];

export type GetStoriesWithDetail3Data = {
    body?: never;
    path?: never;
    query?: never;
    url: '/demo/stories-3';
};

export type GetStoriesWithDetail3Responses = {
    /**
     * Response Get Stories With Detail 3 Demo Stories 3 Get
     *
     * Successful Response
     */
    200: Array<Story3>;
};

export type GetStoriesWithDetail3Response = GetStoriesWithDetail3Responses[keyof GetStoriesWithDetail3Responses];
